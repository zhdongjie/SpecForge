package com.original.business.generated;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.original.core.domain.vo.PageVo;
import com.original.core.domain.vo.ResponseVo;
import com.original.core.service.BusinessJdbcContext;
import com.original.core.utils.SecurityUtils;
import java.sql.*;
import java.time.LocalDateTime;
import java.util.*;
import org.springframework.core.io.ClassPathResource;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.web.bind.annotation.*;

/** Spec-driven business extension. Identifiers originate only from validated compiler metadata. */
@RestController
@RequestMapping("/v1/business")
@PreAuthorize("isAuthenticated()")
public class BusinessResource {
  private final JdbcTemplate db;
  private final TransactionTemplate transactions;
  private final Map<String, Map<String, Object>> entities = new LinkedHashMap<>();

  public BusinessResource(BusinessJdbcContext context, ObjectMapper mapper) throws Exception {
    this.db = context.jdbc();
    this.transactions = context.transactions();
    try (var input = new ClassPathResource("specforge/entities.json").getInputStream()) {
      List<Map<String, Object>> specs = mapper.readValue(input, new TypeReference<>() {});
      for (var e : specs) entities.put((String) e.get("name"), e);
    }
  }

  @SuppressWarnings("unchecked")
  private static Map<String, Object> obj(Object v) {
    return (Map<String, Object>) v;
  }

  @SuppressWarnings("unchecked")
  private static List<Map<String, Object>> fields(Map<String, Object> e) {
    return (List<Map<String, Object>>) e.get("fields");
  }

  private Map<String, Object> reference(Map<String, Object> workflow) {
    return obj(workflow.getOrDefault("exclusive_reference", workflow.get("capacity_reference")));
  }

  private Map<String, Object> referenceField(Map<String, Object> e, Map<String, Object> ref) {
    return fields(e).stream()
        .filter(f -> f.get("name").equals(ref.get("field")))
        .findFirst()
        .orElseThrow();
  }

  private long allocated(
      Map<String, Object> child, Map<String, Object> ref, Object id, boolean lock) {
    var active =
        db.queryForList(
            "SELECT `"
                + ref.get("quantity_field")
                + "` AS amount FROM "
                + table(child)
                + " WHERE `"
                + ref.get("field")
                + "`=? AND status=? AND sf_deleted=0"
                + (lock ? " FOR UPDATE" : ""),
            id,
            ref.get("active_state"));
    long sum = 0;
    for (var record : active) sum = Math.addExact(sum, ((Number) record.get("amount")).longValue());
    return sum;
  }

  /** All workflows sharing a catalog capacity field contribute to the same pool. */
  private long poolUsed(String target, String capacity, Object id, boolean lock) {
    long sum = 0;
    for (var child : entities.values()) {
      if (!child.containsKey("workflow")) continue;
      var w = obj(child.get("workflow"));
      if (!w.containsKey("capacity_reference")) continue;
      var ref = reference(w);
      if (referenceField(child, ref).get("reference").equals(target)
          && ref.get("capacity_field").equals(capacity))
        sum = Math.addExact(sum, allocated(child, ref, id, lock));
    }
    return sum;
  }

  private Set<String> capacityFields(Map<String, Object> target) {
    var result = new LinkedHashSet<String>();
    for (var child : entities.values()) {
      if (!child.containsKey("workflow")) continue;
      var w = obj(child.get("workflow"));
      if (!w.containsKey("capacity_reference")) continue;
      var ref = reference(w);
      if (referenceField(child, ref).get("reference").equals(target.get("name")))
        result.add((String) ref.get("capacity_field"));
    }
    return result;
  }

  /** Availability is derived from active records; returning never increments a mutable counter. */
  private Map<String, Object> availability(Map<String, Object> e, Map<String, Object> record) {
    for (String field : capacityFields(e))
      record.put(
          field + "_available",
          ((Number) record.get(field)).longValue()
              - poolUsed((String) e.get("name"), field, record.get("id"), false));
    return record;
  }

  private Map<String, Object> entity(String name) {
    var e = entities.get(name);
    if (e == null) throw new IllegalArgumentException("业务模块不存在");
    return e;
  }

  private String table(Map<String, Object> e) {
    return "sf_" + e.get("name");
  }

  private boolean has(String permission) {
    return SecurityUtils.getAuthentication().getAuthorities().stream()
        .anyMatch(a -> a.getAuthority().equals(permission));
  }

  private String scope(Map<String, Object> e) {
    return "business:sf_" + e.get("name");
  }

  private void grant(Map<String, Object> e, String action) {
    if (!has(scope(e) + ":" + action)) throw new AccessDeniedException("无操作权限");
  }

  private void crud(Map<String, Object> e, String action) {
    if (!((List<?>) e.get("crud")).contains(action)) throw new AccessDeniedException("不支持该操作");
    grant(e, action);
  }

  private String select(Map<String, Object> e) {
    var c = new ArrayList<String>();
    c.add("id");
    for (var f : fields(e)) c.add("`" + f.get("name") + "`");
    if (e.containsKey("workflow")) {
      c.add("owner_id");
      c.add("status");
    }
    c.add("created_at");
    return String.join(",", c);
  }

  private Map<String, Object> row(Map<String, Object> e, long id, boolean lock) {
    var rows =
        db.queryForList(
            "SELECT "
                + select(e)
                + " FROM "
                + table(e)
                + " WHERE id=? AND sf_deleted=0"
                + (lock ? " FOR UPDATE" : ""),
            id);
    if (rows.isEmpty()) throw new IllegalArgumentException("记录不存在");
    return rows.get(0);
  }

  private boolean ownerOnly(Map<String, Object> e) {
    return e.get("access").equals("owner") && !has(scope(e) + ":manage");
  }

  private void visible(Map<String, Object> e, Map<String, Object> row) {
    if (ownerOnly(e)
        && !Objects.equals(((Number) row.get("owner_id")).longValue(), SecurityUtils.getUserId()))
      throw new AccessDeniedException("无权访问其他申请");
  }

  @GetMapping("/{entity}/page")
  public ResponseVo<PageVo<Map<String, Object>>> page(
      @PathVariable String entity,
      @RequestParam(defaultValue = "1") int currentPage,
      @RequestParam(defaultValue = "20") int pageSize) {
    var e = entity(entity);
    crud(e, "page");
    if (currentPage < 1 || currentPage > 1000000 || pageSize < 1 || pageSize > 100)
      throw new IllegalArgumentException("分页参数无效");
    var params = new ArrayList<Object>();
    String where = " WHERE sf_deleted=0";
    if (ownerOnly(e)) {
      where += " AND owner_id=?";
      params.add(SecurityUtils.getUserId());
    }
    long total =
        db.queryForObject("SELECT COUNT(*) FROM " + table(e) + where, Long.class, params.toArray());
    params.add(pageSize);
    params.add((currentPage - 1) * pageSize);
    return ResponseVo.success(
        new PageVo<>(
            total,
            db
                .queryForList(
                    "SELECT "
                        + select(e)
                        + " FROM "
                        + table(e)
                        + where
                        + " ORDER BY id DESC LIMIT ? OFFSET ?",
                    params.toArray())
                .stream()
                .map(record -> availability(e, record))
                .toList()));
  }

  @GetMapping("/{entity}/{id}")
  public ResponseVo<Map<String, Object>> detail(
      @PathVariable String entity, @PathVariable long id) {
    var e = entity(entity);
    crud(e, "detail");
    var r = row(e, id, false);
    visible(e, r);
    return ResponseVo.success(availability(e, r));
  }

  private LinkedHashMap<String, Object> input(Map<String, Object> e, Map<String, Object> body) {
    var result = new LinkedHashMap<String, Object>();
    var allowed = new HashSet<String>();
    for (var f : fields(e)) allowed.add((String) f.get("name"));
    if (!allowed.containsAll(body.keySet())) throw new IllegalArgumentException("包含不允许修改的字段");
    for (var f : fields(e)) {
      String n = (String) f.get("name"), t = (String) f.get("type");
      Object v = body.containsKey(n) ? body.get(n) : f.get("default");
      if (v == null) {
        if (Boolean.TRUE.equals(f.get("required")))
          throw new IllegalArgumentException(f.get("label") + "不能为空");
        result.put(n, null);
        continue;
      }
      switch (t) {
        case "string", "enum" -> {
          if (!(v instanceof String)
              || ((String) v).length() > 255
              || (Boolean.TRUE.equals(f.get("required")) && ((String) v).isBlank()))
            throw new IllegalArgumentException(f.get("label") + "格式错误");
          if (t.equals("enum") && !((List<?>) f.get("values")).contains(v))
            throw new IllegalArgumentException("枚举值无效");
        }
        case "integer", "foreign" -> {
          try {
            if (v instanceof Float || v instanceof Double) throw new NumberFormatException();
            v = Long.valueOf(v.toString());
          } catch (Exception ex) {
            throw new IllegalArgumentException(f.get("label") + "必须为整数");
          }
        }
        case "boolean" -> {
          if (!(v instanceof Boolean))
            throw new IllegalArgumentException(f.get("label") + "必须为布尔值");
        }
        case "datetime" -> {
          try {
            v = Timestamp.valueOf(LocalDateTime.parse(v.toString()));
          } catch (Exception ex) {
            throw new IllegalArgumentException(f.get("label") + "日期格式错误");
          }
        }
        default -> throw new IllegalArgumentException("不支持的字段类型");
      }
      if (t.equals("integer")
          && f.containsKey("min")
          && ((Number) v).longValue() < ((Number) f.get("min")).longValue())
        throw new IllegalArgumentException(f.get("label") + "不能小于" + f.get("min"));
      if (t.equals("foreign")) {
        String target =
            f.get("reference").equals("system_user") ? "system_user" : "sf_" + f.get("reference");
        if (db.queryForList(
                "SELECT id FROM "
                    + target
                    + " WHERE id=?"
                    + (target.equals("system_user") ? "" : " AND sf_deleted=0")
                    + " FOR UPDATE",
                v)
            .isEmpty()) throw new IllegalArgumentException("关联记录不存在");
      }
      result.put(n, v);
    }
    return result;
  }

  @PostMapping("/{entity}")
  public ResponseVo<Map<String, Object>> create(
      @PathVariable String entity, @RequestBody Map<String, Object> body) {
    return transactions.execute(tx -> createRecord(entity, body));
  }

  private ResponseVo<Map<String, Object>> createRecord(String entity, Map<String, Object> body) {
    var e = entity(entity);
    crud(e, "create");
    var values = input(e, body);
    if (e.containsKey("workflow")) {
      values.put("owner_id", SecurityUtils.getUserId());
      values.put("status", obj(e.get("workflow")).get("initial"));
    }
    var cols = values.keySet().stream().map(k -> "`" + k + "`").toList();
    String sql =
        "INSERT INTO "
            + table(e)
            + " ("
            + String.join(",", cols)
            + ") VALUES ("
            + String.join(",", Collections.nCopies(cols.size(), "?"))
            + ")";
    var keys = new GeneratedKeyHolder();
    db.update(
        connection -> {
          var st = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
          int i = 1;
          for (Object v : values.values()) st.setObject(i++, v);
          return st;
        },
        keys);
    return ResponseVo.success(row(e, Objects.requireNonNull(keys.getKey()).longValue(), false));
  }

  @PutMapping("/{entity}/{id}")
  public ResponseVo<Void> update(
      @PathVariable String entity, @PathVariable long id, @RequestBody Map<String, Object> body) {
    return transactions.execute(tx -> updateRecord(entity, id, body));
  }

  private ResponseVo<Void> updateRecord(String entity, long id, Map<String, Object> body) {
    var e = entity(entity);
    crud(e, "update");
    row(e, id, true);
    var v = input(e, body);
    for (String capacity : capacityFields(e)) {
      long allocated = poolUsed((String) e.get("name"), capacity, id, true);
      if (((Number) v.get(capacity)).longValue() < allocated)
        throw new IllegalArgumentException("总量不能小于当前已占用数量");
    }
    var args = new ArrayList<Object>(v.values());
    args.add(id);
    db.update(
        "UPDATE "
            + table(e)
            + " SET "
            + String.join(",", v.keySet().stream().map(k -> "`" + k + "`=?").toList())
            + " WHERE id=?",
        args.toArray());
    return ResponseVo.success();
  }

  @DeleteMapping("/{entity}/{id}")
  public ResponseVo<Void> delete(@PathVariable String entity, @PathVariable long id) {
    return transactions.execute(tx -> deleteRecord(entity, id));
  }

  private ResponseVo<Void> deleteRecord(String entity, long id) {
    var e = entity(entity);
    crud(e, "delete");
    row(e, id, true);
    for (var other : entities.values())
      for (var f : fields(other))
        if (e.get("name").equals(f.get("reference"))) {
          String extra = "";
          if (other.containsKey("workflow")) {
            var terminals = (List<?>) reference(obj(other.get("workflow"))).get("terminal_states");
            extra =
                " AND status NOT IN ("
                    + String.join(",", Collections.nCopies(terminals.size(), "?"))
                    + ")";
            var args = new ArrayList<Object>();
            args.add(id);
            args.addAll(terminals);
            if (db.queryForObject(
                    "SELECT COUNT(*) FROM "
                        + table(other)
                        + " WHERE `"
                        + f.get("name")
                        + "`=?"
                        + extra,
                    Long.class,
                    args.toArray())
                > 0) throw new IllegalArgumentException("存在未结束申请，无法删除");
          } else if (db.queryForObject(
                  "SELECT COUNT(*) FROM "
                      + table(other)
                      + " WHERE `"
                      + f.get("name")
                      + "`=? AND sf_deleted=0",
                  Long.class,
                  id)
              > 0) throw new IllegalArgumentException("存在关联记录，无法删除");
        }
    db.update("UPDATE " + table(e) + " SET sf_deleted=1 WHERE id=?", id);
    return ResponseVo.success();
  }

  @PostMapping("/{entity}/{id}/actions/{action}")
  public ResponseVo<Void> transition(
      @PathVariable String entity, @PathVariable long id, @PathVariable String action) {
    return transactions.execute(tx -> transitionRecord(entity, id, action));
  }

  private ResponseVo<Void> transitionRecord(String entity, long id, String action) {
    var e = entity(entity);
    grant(e, action);
    if (!e.containsKey("workflow")) throw new IllegalArgumentException("不支持状态操作");
    var w = obj(e.get("workflow"));
    Map<String, Object> transition = null;
    for (Object x : (List<?>) w.get("transitions")) {
      var a = obj(x);
      if (a.get("name").equals(action)) transition = a;
    }
    if (transition == null) throw new IllegalArgumentException("操作不存在");
    // Always lock the shared referenced row first: approvals on different requests serialize.
    var initial = row(e, id, false);
    var ref = reference(w);
    var field = referenceField(e, ref);
    var resource = entity((String) field.get("reference"));
    var catalog = row(resource, ((Number) initial.get(ref.get("field"))).longValue(), true);
    var current = row(e, id, true);
    if (Boolean.TRUE.equals(transition.get("forbid_self"))
        && Objects.equals(
            ((Number) current.get("owner_id")).longValue(), SecurityUtils.getUserId()))
      throw new IllegalArgumentException("不能审批自己的申请");
    if (!transition.get("from").equals(current.get("status")))
      throw new IllegalArgumentException("当前状态不允许此操作");
    if (ref.get("active_state").equals(transition.get("to"))) {
      if (w.containsKey("capacity_reference")) {
        String capacity = (String) ref.get("capacity_field");
        long total = ((Number) catalog.get(capacity)).longValue();
        long used = poolUsed((String) resource.get("name"), capacity, catalog.get("id"), true);
        long requested = ((Number) current.get(ref.get("quantity_field"))).longValue();
        if (requested > total - used) throw new IllegalArgumentException("可用数量不足");
      } else {
        var active =
            db.queryForList(
                "SELECT id FROM "
                    + table(e)
                    + " WHERE `"
                    + ref.get("field")
                    + "`=? AND status=? FOR UPDATE",
                current.get(ref.get("field")),
                ref.get("active_state"));
        if (!active.isEmpty()) throw new IllegalArgumentException("关联资源已被占用");
      }
    }
    if (db.update(
            "UPDATE " + table(e) + " SET status=? WHERE id=? AND status=?",
            transition.get("to"),
            id,
            transition.get("from"))
        != 1) throw new IllegalArgumentException("状态已变化，请刷新");
    return ResponseVo.success();
  }

  @ExceptionHandler({IllegalArgumentException.class, DataIntegrityViolationException.class})
  public ResponseEntity<ResponseVo<Void>> invalid(Exception ex) {
    return ResponseEntity.badRequest()
        .body(
            ResponseVo.fail(
                ex instanceof DataIntegrityViolationException ? "数据重复或存在关联记录" : ex.getMessage()));
  }
}
