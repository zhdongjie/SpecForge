package com.original.business.recipes;

import com.original.core.config.properties.OriginalProperties;
import com.original.core.domain.vo.PageVo;
import com.original.core.domain.vo.ResponseVo;
import com.original.core.enums.FileBusinessType;
import com.original.core.utils.SecurityUtils;
import com.original.system.file.manager.FileManager;
import com.original.system.file.service.FileReferenceService;
import com.original.system.file.service.ImageValidationService;
import java.net.URI;
import java.sql.Statement;
import java.util.*;
import org.apache.ibatis.session.SqlSessionFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.transaction.annotation.TransactionManagementConfigurer;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

/** Recipe application boundary. Raw generated entity endpoints receive no grants. */
@RestController
@RequestMapping("/v1/recipes")
@PreAuthorize("isAuthenticated()")
public class RecipeResource {
  private final JdbcTemplate db;
  private final TransactionTemplate tx;
  private final FileManager files;
  private final ImageValidationService images;
  private final FileReferenceService references;
  private final OriginalProperties properties;
  private static final String COVER_PREFIX = "/api/files";

  public RecipeResource(
      SqlSessionFactory sessions,
      TransactionManagementConfigurer management,
      FileManager files,
      FileReferenceService references,
      OriginalProperties properties,
      ImageValidationService images) {
    this.images = images;
    this.files = files;
    this.references = references;
    this.properties = properties;
    this.db = new JdbcTemplate(sessions.getConfiguration().getEnvironment().getDataSource());
    var manager = management.annotationDrivenTransactionManager();
    if (!(manager instanceof org.springframework.transaction.PlatformTransactionManager platform)) {
      throw new IllegalArgumentException(
          "Template must provide an imperative platform transaction manager");
    }
    this.tx = new TransactionTemplate(platform);
  }

  private boolean has(String action) {
    return SecurityUtils.getAuthentication().getAuthorities().stream()
        .anyMatch(a -> a.getAuthority().equals("business:recipes:" + action));
  }

  private void grant(String action) {
    if (!has(action)) throw new AccessDeniedException("无操作权限");
  }

  private long user() {
    return SecurityUtils.getUserId();
  }

  private void only(Map<String, Object> body, Set<String> keys) {
    if (!keys.containsAll(body.keySet())) throw new IllegalArgumentException("包含不允许修改的字段");
  }

  private String text(Object value, int max, boolean required, String label) {
    if (value == null && !required) return "";
    if (!(value instanceof String)) throw new IllegalArgumentException(label + "格式错误");
    String result = ((String) value).strip();
    if (result.length() > max || (required && result.isEmpty()))
      throw new IllegalArgumentException(label + "长度不符合要求");
    return result;
  }

  private long number(Object value, long min, long max, String label) {
    try {
      if (value == null || !value.toString().matches("[0-9]+")) throw new NumberFormatException();
      long result = Long.parseLong(value.toString());
      if (result < min || result > max) throw new NumberFormatException();
      return result;
    } catch (Exception ex) {
      throw new IllegalArgumentException(label + "必须为有效整数");
    }
  }

  private Map<String, Object> row(long id, boolean lock) {
    var list =
        db.queryForList(
            "SELECT * FROM sf_recipe WHERE id=? AND sf_deleted=0" + (lock ? " FOR UPDATE" : ""),
            id);
    if (list.isEmpty()) throw new IllegalArgumentException("菜谱不存在");
    return list.get(0);
  }

  private boolean owner(Map<String, Object> row) {
    return ((Number) row.get("author_id")).longValue() == user();
  }

  private void author(Map<String, Object> row) {
    if (!owner(row)) throw new AccessDeniedException("只能修改自己的菜谱");
  }

  private void version(Map<String, Object> row, Map<String, Object> body) {
    if (number(body.get("revision"), 1, Long.MAX_VALUE, "修订号")
        != ((Number) row.get("revision")).longValue())
      throw new IllegalArgumentException("菜谱已更新，请刷新后重试");
  }

  private void readable(Map<String, Object> row) {
    if (!"PUBLISHED".equals(row.get("publication_state")) && !owner(row) && !has("review"))
      throw new AccessDeniedException("菜谱尚未发布");
  }

  @GetMapping("/categories")
  public ResponseVo<List<Map<String, Object>>> categories() {
    grant("browse");
    return ResponseVo.success(
        db.queryForList("SELECT id,name FROM sf_recipe_category WHERE sf_deleted=0 ORDER BY id"));
  }

  @GetMapping("/page")
  public ResponseVo<PageVo<Map<String, Object>>> page(
      @RequestParam(defaultValue = "published") String view,
      @RequestParam(defaultValue = "") String keyword,
      @RequestParam(required = false) Long categoryId,
      @RequestParam(defaultValue = "1") int currentPage,
      @RequestParam(defaultValue = "12") int pageSize) {
    grant("browse");
    if (currentPage < 1
        || currentPage > 1000000
        || pageSize < 1
        || pageSize > 50
        || keyword.length() > 80) throw new IllegalArgumentException("查询参数无效");
    var args = new ArrayList<Object>();
    String where = " WHERE r.sf_deleted=0";
    switch (view) {
      case "published" -> where += " AND r.publication_state='PUBLISHED'";
      case "mine" -> {
        grant("publish");
        where += " AND r.author_id=?";
        args.add(user());
      }
      case "favorites" -> {
        grant("favorite");
        where +=
            " AND r.publication_state='PUBLISHED' AND EXISTS(SELECT 1 FROM sf_recipe_favorite f"
                + " WHERE f.recipe_id=r.id AND f.user_id=? AND f.sf_deleted=0)";
        args.add(user());
      }
      case "review" -> {
        grant("review");
        where += " AND r.publication_state='PENDING'";
      }
      default -> throw new IllegalArgumentException("不支持的列表");
    }
    if (categoryId != null) {
      where += " AND r.category_id=?";
      args.add(categoryId);
    }
    if (!keyword.isBlank()) {
      where += " AND (r.title LIKE ? ESCAPE '!' OR r.summary LIKE ? ESCAPE '!')";
      String term =
          "%" + keyword.strip().replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%";
      args.add(term);
      args.add(term);
    }
    long total =
        db.queryForObject("SELECT COUNT(*) FROM sf_recipe r" + where, Long.class, args.toArray());
    args.add(pageSize);
    args.add((currentPage - 1) * pageSize);
    var rows =
        db.queryForList(
            "SELECT r.*,c.name AS category_name,u.username AS author_name FROM sf_recipe r JOIN"
                + " sf_recipe_category c ON c.id=r.category_id JOIN system_user u ON"
                + " u.id=r.author_id"
                + where
                + " ORDER BY r.id DESC LIMIT ? OFFSET ?",
            args.toArray());
    rows.forEach(this::decorate);
    return ResponseVo.success(new PageVo<>(total, rows));
  }

  private Map<String, Object> decorate(Map<String, Object> record) {
    record.remove("sf_deleted");
    record.put("mine", owner(record));
    record.put(
        "favorite",
        db.queryForObject(
                "SELECT COUNT(*) FROM sf_recipe_favorite WHERE recipe_id=? AND user_id=? AND"
                    + " sf_deleted=0",
                Long.class,
                record.get("id"),
                user())
            > 0);
    return record;
  }

  @GetMapping("/{id}")
  public ResponseVo<Map<String, Object>> detail(@PathVariable long id) {
    grant("browse");
    // Keep visibility and ingredient/step reads together so a concurrent author edit
    // cannot combine published metadata with newly withdrawn, unreviewed children.
    return tx.execute(
        status -> {
          var record = row(id, true);
          readable(record);
          record.put(
              "ingredients",
              db.queryForList(
                  "SELECT name,amount FROM sf_recipe_ingredient WHERE recipe_id=? ORDER BY"
                      + " position",
                  id));
          record.put(
              "steps",
              db
                  .queryForList(
                      "SELECT instruction FROM sf_recipe_step WHERE recipe_id=? ORDER BY position",
                      id)
                  .stream()
                  .map(step -> step.get("instruction"))
                  .toList());
          return ResponseVo.success(decorate(record));
        });
  }

  /**
   * Reuse the platform uploader while keeping recipe-publish authority independent of file admin.
   */
  @PostMapping("/cover")
  public ResponseVo<Map<String, String>> uploadCover(@RequestParam("file") MultipartFile file)
      throws Exception {
    grant("publish");
    images.validate(file, new ImageValidationService.Policy(5L * 1024 * 1024, 4096, 128));
    String uploaded = files.upload(List.of(file)).getData().get(0);
    String prefix = properties.upload().requestUrl();
    if (!uploaded.startsWith(prefix + "/")) throw new IllegalArgumentException("上传服务返回了无效文件路径");
    return ResponseVo.success(
        Map.of(
            "url",
            COVER_PREFIX + uploaded.substring(prefix.length()),
            "name",
            file.getOriginalFilename()));
  }

  private void validateCover(String cover) {
    if (!cover.startsWith(COVER_PREFIX + "/")) return;
    String relative = cover.substring(COVER_PREFIX.length());
    var rows =
        db.queryForList(
            "SELECT id,created_by,mime_type FROM system_file WHERE file_url=? FOR UPDATE",
            relative);
    if (rows.size() != 1
        || rows.get(0).get("created_by") == null
        || ((Number) rows.get(0).get("created_by")).longValue() != user()
        || !Set.of("image/png", "image/jpeg").contains(rows.get(0).get("mime_type")))
      throw new IllegalArgumentException("封面必须是本人上传且仍存在的图片");
  }

  private void syncCover(long recipe, String cover) {
    references.updateFileReference(
        recipe,
        cover.startsWith(COVER_PREFIX + "/")
            ? properties.upload().requestUrl() + cover.substring(COVER_PREFIX.length())
            : null,
        FileBusinessType.RECIPE_COVER);
  }

  private Map<String, Object> draft(Map<String, Object> body, boolean update) {
    var allowed =
        new HashSet<>(
            Set.of(
                "title",
                "summary",
                "category_id",
                "servings",
                "prep_minutes",
                "cover_url",
                "ingredients",
                "steps"));
    if (update) allowed.add("revision");
    only(body, allowed);
    var values = new LinkedHashMap<String, Object>();
    values.put("title", text(body.get("title"), 80, true, "菜名"));
    values.put("summary", text(body.get("summary"), 255, false, "简介"));
    long category = number(body.get("category_id"), 1, Long.MAX_VALUE, "分类");
    if (db.queryForList(
            "SELECT id FROM sf_recipe_category WHERE id=? AND sf_deleted=0 FOR UPDATE", category)
        .isEmpty()) throw new IllegalArgumentException("分类不存在");
    values.put("category_id", category);
    values.put("servings", number(body.getOrDefault("servings", 1), 1, 100, "份数"));
    values.put("prep_minutes", number(body.getOrDefault("prep_minutes", 0), 0, 1440, "准备时间"));
    String cover = text(body.get("cover_url"), 255, false, "封面");
    if (!cover.isEmpty() && !cover.startsWith(COVER_PREFIX + "/")) {
      try {
        URI uri = URI.create(cover);
        if (!"https".equalsIgnoreCase(uri.getScheme())
            || uri.getHost() == null
            || uri.getUserInfo() != null
            || uri.getPath().startsWith(COVER_PREFIX + "/")) throw new IllegalArgumentException();
      } catch (Exception ex) {
        throw new IllegalArgumentException("封面必须是本系统上传图片或 HTTPS 图片地址");
      }
    }
    values.put("cover_url", cover);
    if (!(body.get("ingredients") instanceof List<?> ingredients)
        || ingredients.isEmpty()
        || ingredients.size() > 40) throw new IllegalArgumentException("请填写 1 至 40 项食材");
    for (Object item : ingredients) {
      if (!(item instanceof Map<?, ?> ingredient)
          || !Set.of("name", "amount").containsAll(ingredient.keySet()))
        throw new IllegalArgumentException("食材格式错误");
      text(ingredient.get("name"), 80, true, "食材名称");
      text(ingredient.get("amount"), 80, true, "食材用量");
    }
    if (!(body.get("steps") instanceof List<?> steps) || steps.isEmpty() || steps.size() > 40)
      throw new IllegalArgumentException("请填写 1 至 40 个步骤");
    for (Object step : steps) text(step, 255, true, "步骤");
    return values;
  }

  private void children(long id, Map<String, Object> body) {
    db.update("DELETE FROM sf_recipe_ingredient WHERE recipe_id=?", id);
    db.update("DELETE FROM sf_recipe_step WHERE recipe_id=?", id);
    int pos = 0;
    for (Object item : (List<?>) body.get("ingredients")) {
      var value = (Map<?, ?>) item;
      db.update(
          "INSERT INTO sf_recipe_ingredient(recipe_id,name,amount,position) VALUES(?,?,?,?)",
          id,
          text(value.get("name"), 80, true, "食材"),
          text(value.get("amount"), 80, true, "用量"),
          ++pos);
    }
    pos = 0;
    for (Object step : (List<?>) body.get("steps"))
      db.update(
          "INSERT INTO sf_recipe_step(recipe_id,instruction,position) VALUES(?,?,?)",
          id,
          text(step, 255, true, "步骤"),
          ++pos);
  }

  @PostMapping
  public ResponseVo<Map<String, Object>> create(@RequestBody Map<String, Object> body) {
    grant("publish");
    return tx.execute(
        status -> {
          var values = draft(body, false);
          validateCover((String) values.get("cover_url"));
          values.put("author_id", user());
          values.put("publication_state", "DRAFT");
          values.put("revision", 1);
          var keys = new GeneratedKeyHolder();
          db.update(
              connection -> {
                var statement =
                    connection.prepareStatement(
                        "INSERT INTO sf_recipe ("
                            + String.join(",", values.keySet())
                            + ") VALUES ("
                            + String.join(",", Collections.nCopies(values.size(), "?"))
                            + ")",
                        Statement.RETURN_GENERATED_KEYS);
                int i = 1;
                for (Object value : values.values()) statement.setObject(i++, value);
                return statement;
              },
              keys);
          long id = Objects.requireNonNull(keys.getKey()).longValue();
          children(id, body);
          syncCover(id, (String) values.get("cover_url"));
          return ResponseVo.success(decorate(row(id, false)));
        });
  }

  @PutMapping("/{id}")
  public ResponseVo<Void> update(@PathVariable long id, @RequestBody Map<String, Object> body) {
    grant("publish");
    return tx.execute(
        status -> {
          // Category-before-recipe lock order also matches category deletion in the generic
          // controller.
          var values = draft(body, true);
          var record = row(id, true);
          author(record);
          version(record, body);
          if ("PENDING".equals(record.get("publication_state")))
            throw new IllegalArgumentException("待审核菜谱不能编辑");
          validateCover((String) values.get("cover_url"));
          var args = new ArrayList<Object>(values.values());
          args.add(id);
          args.add(record.get("revision"));
          if (db.update(
                  "UPDATE sf_recipe SET "
                      + String.join(",", values.keySet().stream().map(k -> k + "=?").toList())
                      + ",publication_state='DRAFT',review_reason=NULL,revision=revision+1 WHERE"
                      + " id=? AND revision=?",
                  args.toArray())
              != 1) throw new IllegalArgumentException("菜谱已更新");
          children(id, body);
          syncCover(id, (String) values.get("cover_url"));
          return ResponseVo.success();
        });
  }

  @DeleteMapping("/{id}")
  public ResponseVo<Void> delete(@PathVariable long id, @RequestParam long revision) {
    grant("publish");
    return tx.execute(
        status -> {
          var record = row(id, true);
          author(record);
          version(record, Map.of("revision", revision));
          if ("PENDING".equals(record.get("publication_state")))
            throw new IllegalArgumentException("待审核菜谱不能删除");
          references.deleteFileReference(id, FileBusinessType.RECIPE_COVER);
          db.update("UPDATE sf_recipe SET sf_deleted=1,revision=revision+1 WHERE id=?", id);
          return ResponseVo.success();
        });
  }

  @PostMapping("/{id}/actions/{action}")
  public ResponseVo<Void> action(
      @PathVariable long id, @PathVariable String action, @RequestBody Map<String, Object> body) {
    if (!Set.of("submit", "approve", "reject").contains(action))
      throw new IllegalArgumentException("不支持的操作");
    grant(action.equals("submit") ? "publish" : "review");
    only(body, Set.of("revision", "reason"));
    return tx.execute(
        status -> {
          var record = row(id, true);
          version(record, body);
          String current = (String) record.get("publication_state");
          String target;
          String reason = "";
          if (action.equals("submit")) {
            author(record);
            if (!Set.of("DRAFT", "REJECTED").contains(current))
              throw new IllegalArgumentException("当前状态不能提交");
            target = "PENDING";
          } else {
            if (owner(record)) throw new IllegalArgumentException("不能审核自己的菜谱");
            if (!"PENDING".equals(current)) throw new IllegalArgumentException("当前状态不能审核");
            target = action.equals("approve") ? "PUBLISHED" : "REJECTED";
            if (action.equals("reject")) reason = text(body.get("reason"), 255, true, "驳回原因");
          }
          if (db.update(
                  "UPDATE sf_recipe SET publication_state=?,review_reason=?,revision=revision+1"
                      + " WHERE id=? AND revision=? AND publication_state=?",
                  target,
                  reason,
                  id,
                  record.get("revision"),
                  current)
              != 1) throw new IllegalArgumentException("菜谱已变化，请刷新");
          return ResponseVo.success();
        });
  }

  @PostMapping("/{id}/favorite")
  public ResponseVo<Void> favorite(@PathVariable long id) {
    grant("browse");
    grant("favorite");
    return tx.execute(
        status -> {
          var record = row(id, true);
          if (!"PUBLISHED".equals(record.get("publication_state")))
            throw new IllegalArgumentException("只能收藏已发布菜谱");
          db.update(
              "INSERT INTO sf_recipe_favorite(recipe_id,user_id) VALUES(?,?) ON DUPLICATE KEY"
                  + " UPDATE sf_deleted=0",
              id,
              user());
          return ResponseVo.success();
        });
  }

  @DeleteMapping("/{id}/favorite")
  public ResponseVo<Void> unfavorite(@PathVariable long id) {
    grant("favorite");
    db.update(
        "UPDATE sf_recipe_favorite SET sf_deleted=1 WHERE recipe_id=? AND user_id=?", id, user());
    return ResponseVo.success();
  }

  @GetMapping("/statistics")
  public ResponseVo<Map<String, Object>> statistics() {
    grant("statistics");
    var result = new LinkedHashMap<String, Object>();
    result.put("users", db.queryForObject("SELECT COUNT(*) FROM system_user", Long.class));
    result.put(
        "published",
        db.queryForObject(
            "SELECT COUNT(*) FROM sf_recipe WHERE publication_state='PUBLISHED' AND sf_deleted=0",
            Long.class));
    result.put(
        "pending",
        db.queryForObject(
            "SELECT COUNT(*) FROM sf_recipe WHERE publication_state='PENDING' AND sf_deleted=0",
            Long.class));
    result.put(
        "favorites",
        db.queryForObject(
            "SELECT COUNT(*) FROM sf_recipe_favorite f JOIN sf_recipe r ON r.id=f.recipe_id WHERE"
                + " f.sf_deleted=0 AND r.sf_deleted=0 AND r.publication_state='PUBLISHED'",
            Long.class));
    result.put(
        "categories",
        db.queryForList(
            "SELECT c.name,COUNT(r.id) AS count FROM sf_recipe_category c LEFT JOIN sf_recipe r ON"
                + " r.category_id=c.id AND r.sf_deleted=0 AND r.publication_state='PUBLISHED' WHERE"
                + " c.sf_deleted=0 GROUP BY c.id,c.name ORDER BY c.id"));
    return ResponseVo.success(result);
  }

  @ExceptionHandler({IllegalArgumentException.class, DataIntegrityViolationException.class})
  public ResponseEntity<ResponseVo<Void>> invalid(Exception error) {
    return ResponseEntity.badRequest()
        .body(
            ResponseVo.fail(
                error instanceof DataIntegrityViolationException
                    ? "数据重复或关联记录已变化"
                    : error.getMessage()));
  }
}
