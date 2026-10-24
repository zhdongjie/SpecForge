const fs = require("fs"),
  path = require("path");
(async () => {
  const cfg = JSON.parse(fs.readFileSync(0, "utf8"));
  const { withBrowser } = require(cfg.support);
  await withBrowser(cfg, async ({ session, visible, absent, mark, assert }) => {
    const author = await session("sfchef");
    await author.goto(cfg.origin + "/business/recipes");
    await visible(
      author.getByRole("heading", { name: "食谱厨房", exact: true }),
    );
    await author.getByRole("button", { name: "发布菜谱", exact: true }).click();
    let dialog = author.getByRole("dialog");
    await dialog.getByLabel("菜名", { exact: true }).fill(cfg.recipe_title);
    await dialog
      .getByLabel("简介", { exact: true })
      .fill("番茄与鸡蛋，一道熟悉的家常味道。");
    await dialog.getByLabel("食材名称 1", { exact: true }).fill("番茄");
    await dialog.getByLabel("食材用量 1", { exact: true }).fill("2 个");
    await dialog.getByRole("button", { name: "添加食材", exact: true }).click();
    await dialog.getByLabel("食材名称 2", { exact: true }).fill("鸡蛋");
    await dialog.getByLabel("食材用量 2", { exact: true }).fill("3 个");
    await dialog
      .getByLabel("步骤 1", { exact: true })
      .fill("番茄洗净切块，鸡蛋打散。");
    await dialog.getByRole("button", { name: "添加步骤", exact: true }).click();
    await dialog
      .getByLabel("步骤 2", { exact: true })
      .fill("热锅炒熟鸡蛋，加入番茄翻炒，加盐调味。");
    await dialog.getByTestId("cover-upload").setInputFiles({
      name: "browser-cover.png",
      mimeType: "image/png",
      buffer: Buffer.from(cfg.png_fixture, "base64"),
    });
    const previewImage = dialog.getByTestId("cover-preview");
    await previewImage.waitFor({ state: "visible" });
    await previewImage.evaluate((img) => img.decode());
    assert.ok(await previewImage.evaluate((img) => img.naturalWidth > 0));
    mark("author uploads and previews real cover image");
    await dialog.getByRole("button", { name: "保存草稿", exact: true }).click();
    let card = author.locator("article").filter({ hasText: cfg.recipe_title });
    await visible(card.getByText("草稿", { exact: true }));
    await card.getByRole("button", { name: "提交审核", exact: true }).click();
    await visible(card.getByText("待审核", { exact: true }));
    mark("author creates ingredient and step details and submits draft");
    const admin = await session("sfadmin");
    await admin.goto(cfg.origin + "/business/recipes");
    await admin.getByRole("button", { name: "待审核", exact: true }).click();
    let review = admin.locator("article").filter({ hasText: cfg.recipe_title });
    await review.getByRole("button", { name: "查看做法", exact: true }).click();
    let preview = admin.getByRole("dialog");
    await visible(preview.getByText("番茄 — 2 个", { exact: true }));
    await visible(
      preview.getByText("番茄洗净切块，鸡蛋打散。", { exact: true }),
    );
    await preview.getByRole("button", { name: "关闭", exact: true }).click();
    await review.getByRole("button", { name: "通过", exact: true }).click();
    await absent(review);
    mark("reviewer inspects complete recipe details and approves");
    const reader = await session("sfguest");
    await reader.goto(cfg.origin + "/business/recipes");
    await reader
      .getByLabel("搜索菜名或简介", { exact: true })
      .fill(cfg.recipe_title);
    await reader.getByRole("button", { name: "搜索", exact: true }).click();
    let published = reader
      .locator("article")
      .filter({ hasText: cfg.recipe_title });
    await visible(published);
    await published
      .locator('img[alt="菜谱封面"]')
      .evaluate((img) => img.decode());
    assert.ok(
      await published
        .locator('img[alt="菜谱封面"]')
        .evaluate((img) => img.naturalWidth > 0),
    );
    mark("published recipe renders uploaded cover");
    await published.getByRole("button", { name: "收藏", exact: true }).click();
    await visible(
      published.getByRole("button", { name: "取消收藏", exact: true }),
    );
    await reader.getByRole("button", { name: "我的收藏", exact: true }).click();
    await visible(published);
    mark("reader searches published recipe and favorites it");
    await author.getByRole("button", { name: "我的发布", exact: true }).click();
    card = author.locator("article").filter({ hasText: cfg.recipe_title });
    await card.getByRole("button", { name: "编辑", exact: true }).click();
    dialog = author.getByRole("dialog");
    assert.equal(
      await dialog.getByLabel("食材名称 2", { exact: true }).inputValue(),
      "鸡蛋",
    );
    await visible(dialog.getByTestId("cover-preview"));
    const previousCover = await dialog
      .getByTestId("cover-preview")
      .getAttribute("src");
    await dialog.getByTestId("cover-upload").setInputFiles({
      name: "replacement.png",
      mimeType: "image/png",
      buffer: Buffer.from(cfg.png_fixture, "base64"),
    });
    await author.waitForFunction(
      (previous) =>
        document
          .querySelector('[data-testid="cover-preview"]')
          ?.getAttribute("src") !== previous,
      previousCover,
    );
    await dialog.getByTestId("cover-preview").evaluate((img) => img.decode());
    mark("author reopens and replaces uploaded cover");
    await dialog
      .getByLabel("简介", { exact: true })
      .fill("加入完整调味说明，重新提交审核。");
    await dialog.getByRole("button", { name: "保存草稿", exact: true }).click();
    await visible(card.getByText("草稿", { exact: true }));
    await reader.getByRole("button", { name: "搜索", exact: true }).click();
    await absent(published);
    mark(
      "published edit preserves details and withdraws content from favorites",
    );
    await card.getByRole("button", { name: "提交审核", exact: true }).click();
    await visible(card.getByText("待审核", { exact: true }));
    await admin.getByRole("button", { name: "待审核", exact: true }).click();
    review = admin.locator("article").filter({ hasText: cfg.recipe_title });
    await review.getByRole("button", { name: "驳回", exact: true }).click();
    let rejection = admin.getByRole("dialog");
    await rejection
      .getByLabel("驳回原因", { exact: true })
      .fill("请说明盐的用量");
    await rejection
      .getByRole("button", { name: "确认驳回", exact: true })
      .click();
    await absent(review);
    await author.getByRole("button", { name: "我的发布", exact: true }).click();
    await visible(card.getByText("已驳回", { exact: true }));
    await visible(card.getByText("驳回原因：请说明盐的用量", { exact: true }));
    await card.getByRole("button", { name: "编辑", exact: true }).click();
    dialog = author.getByRole("dialog");
    await dialog
      .getByLabel("步骤 2", { exact: true })
      .fill("热锅炒熟鸡蛋，加入番茄，加盐 2 克翻炒均匀。");
    await dialog.getByRole("button", { name: "保存草稿", exact: true }).click();
    await visible(card.getByText("草稿", { exact: true }));
    await card.getByRole("button", { name: "提交审核", exact: true }).click();
    await visible(card.getByText("待审核", { exact: true }));
    await admin.getByRole("button", { name: "待审核", exact: true }).click();
    review = admin.locator("article").filter({ hasText: cfg.recipe_title });
    await review.getByRole("button", { name: "通过", exact: true }).click();
    await absent(review);
    await reader.getByRole("button", { name: "搜索", exact: true }).click();
    await visible(published);
    mark(
      "rejection reason, author correction and resubmission restore publication",
    );
    await published
      .getByRole("button", { name: "取消收藏", exact: true })
      .click();
    await absent(published);
    await reader.getByRole("button", { name: "发现菜谱", exact: true }).click();
    await visible(
      reader.locator("article").filter({ hasText: cfg.recipe_title }),
    );
    await reader.getByLabel("搜索菜名或简介", { exact: true }).fill("");
    await reader.getByRole("button", { name: "搜索", exact: true }).click();
    await reader.screenshot({
      path: path.join(cfg.reports, "browser-recipes.png"),
      fullPage: true,
    });
    mark("reader cancels favorite and returns to recipe discovery");
    await admin.goto(cfg.origin + "/business/recipe_stats");
    await visible(
      admin.getByRole("heading", { name: "食谱统计", exact: true }),
    );
    await visible(admin.getByText("已发布菜谱分类分布", { exact: true }));
    await admin.screenshot({
      path: path.join(cfg.reports, "browser-statistics.png"),
      fullPage: true,
    });
    mark("administrator statistics dashboard accessible");
    const readonly = await session("sfread");
    await readonly.goto(cfg.origin + "/business/recipes");
    await visible(
      readonly.getByRole("heading", { name: "食谱厨房", exact: true }),
    );
    for (const name of ["发布菜谱", "我的收藏", "我的发布", "待审核", "收藏"])
      await absent(readonly.getByRole("button", { name, exact: true }));
    mark("readonly account has browsing without mutation controls");
    const none = await session("sfnone");
    await none.goto(cfg.origin + "/business/recipes");
    await none.waitForURL("**/error-403");
    mark("no-access account denied recipe route");
    await reader.setViewportSize({ width: 390, height: 844 });
    await reader.waitForFunction(
      () =>
        document.querySelector(".recipe-shell").getBoundingClientRect().width >=
        window.innerWidth - 64,
    );
    await reader.screenshot({
      path: path.join(cfg.reports, "browser-recipes-mobile.png"),
      fullPage: true,
    });
    assert.ok(
      await reader.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth + 1,
      ),
    );
    mark("mobile recipe discovery has no horizontal overflow");
  });
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
