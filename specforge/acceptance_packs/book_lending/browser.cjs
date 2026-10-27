const fs = require("fs"),
  path = require("path");
(async () => {
  const cfg = JSON.parse(fs.readFileSync(0, "utf8"));
  const { withBrowser } = require(cfg.support);
  const defs = Object.fromEntries(cfg.entities.map((e) => [e.name, e]));
  const label = (name) =>
    defs.loan.workflow.transitions.find((a) => a.name === name).label;
  const state = (name) => defs.loan.workflow.state_labels?.[name] || name;
  await withBrowser(cfg, async ({ session, visible, absent, mark, assert }) => {
    const admin = await session("sfadmin");
    await admin.goto(cfg.origin + "/business/sf_book");
    await admin
      .getByRole("button", { name: "新增" + defs.book.label, exact: true })
      .click();
    let dialog = admin.getByRole("dialog");
    await dialog.getByRole("button", { name: "保存", exact: true }).click();
    await visible(dialog.getByText("请检查标红字段后再保存", { exact: true }));
    await visible(dialog.getByText("请填写图书编号", { exact: true }));
    await dialog.getByTestId("field-code").locator("input").fill(cfg.book.code);
    await dialog.getByTestId("field-name").locator("input").fill(cfg.book.name);
    await dialog
      .getByTestId("field-stock")
      .locator("input")
      .fill(String(cfg.book.stock));
    await dialog.getByTestId("field-stock").locator("input").fill("-1");
    await dialog.getByRole("button", { name: "保存", exact: true }).click();
    await visible(dialog.getByText("不能小于 0", { exact: true }));
    await dialog
      .getByTestId("field-stock")
      .locator("input")
      .fill(String(cfg.book.stock));
    mark("generic form validates required fields and nonnegative integers");
    if (cfg.field_case) {
      await dialog
        .getByTestId("field-" + cfg.field_case.field)
        .locator("input")
        .fill(cfg.field_case.value);
      if (cfg.field_case.shelf) {
        assert.equal(
          await dialog
            .getByTestId("field-shelf_number")
            .locator("input")
            .inputValue(),
          "0",
        );
        await dialog
          .getByTestId("field-shelf_number")
          .locator("input")
          .fill("8");
      } else {
        await visible(dialog.getByLabel("馆藏名称", { exact: true }));
        await absent(dialog.getByTestId("field-isbn"));
        await absent(dialog.getByTestId("field-shelf_number"));
      }
    }
    await dialog.getByRole("button", { name: "保存", exact: true }).click();
    await visible(
      admin.getByRole("cell", { name: cfg.book.code, exact: true }),
    );
    mark("admin creates book with stock two");
    if (cfg.field_case) {
      const fieldRow = admin
        .getByRole("row")
        .filter({ hasText: cfg.book.code });
      await visible(
        fieldRow.getByRole("cell", { name: cfg.field_case.value, exact: true }),
      );
      await fieldRow.getByRole("button", { name: "编辑", exact: true }).click();
      dialog = admin.getByRole("dialog");
      assert.equal(
        await dialog
          .getByTestId("field-" + cfg.field_case.field)
          .locator("input")
          .inputValue(),
        cfg.field_case.value,
      );
      if (cfg.field_case.shelf)
        assert.equal(
          await dialog
            .getByTestId("field-shelf_number")
            .locator("input")
            .inputValue(),
          "8",
        );
      await dialog.getByRole("button", { name: "取消", exact: true }).click();
      mark("field scenario form list persistence and reopen verified");
    }
    const reader = await session("liba");
    await reader.goto(cfg.origin + "/business/sf_loan");
    await reader
      .getByRole("button", { name: "新增" + defs.loan.label, exact: true })
      .click();
    dialog = reader.getByRole("dialog");
    await dialog.getByTestId("field-book_id").locator(".v-field").click();
    await reader
      .getByRole("option", { name: cfg.book.name, exact: true })
      .click();
    await dialog.getByTestId("field-quantity").locator("input").fill("2");
    await dialog
      .getByTestId("field-reason")
      .locator("input")
      .fill("浏览器数量借阅");
    await dialog.getByRole("button", { name: "保存", exact: true }).click();
    await visible(
      reader.getByRole("cell", { name: "浏览器数量借阅", exact: true }),
    );
    await absent(
      reader.getByRole("button", { name: label("approve"), exact: true }),
    );
    mark("reader submits quantity two without approval controls");
    await admin.goto(cfg.origin + "/business/sf_loan");
    let row = admin.getByRole("row").filter({ hasText: "浏览器数量借阅" });
    await row
      .getByRole("button", { name: label("approve"), exact: true })
      .click();
    await admin
      .getByRole("dialog")
      .getByRole("button", { name: "确认", exact: true })
      .click();
    await visible(
      row.getByRole("cell", { name: state("APPROVED"), exact: true }),
    );
    await admin.goto(cfg.origin + "/business/sf_book");
    let catalog = admin.getByRole("row").filter({ hasText: cfg.book.name });
    await visible(
      catalog
        .getByTestId("availability-stock_available")
        .filter({ hasText: /^\s*0\s*$/ }),
    );
    mark("approval consumes exactly two stock units in the UI");
    await admin.goto(cfg.origin + "/business/sf_loan");
    row = admin.getByRole("row").filter({ hasText: "浏览器数量借阅" });
    await row
      .getByRole("button", { name: label("return_books"), exact: true })
      .click();
    await admin
      .getByRole("dialog")
      .getByRole("button", { name: "确认", exact: true })
      .click();
    await visible(
      row.getByRole("cell", { name: state("RETURNED"), exact: true }),
    );
    await admin.goto(cfg.origin + "/business/sf_book");
    catalog = admin.getByRole("row").filter({ hasText: cfg.book.name });
    await visible(
      catalog
        .getByTestId("availability-stock_available")
        .filter({ hasText: /^\s*2\s*$/ }),
    );
    mark("return restores availability without inflating total stock");
    await admin.screenshot({
      path: path.join(cfg.reports, "browser-admin.png"),
      fullPage: true,
    });
    const readonly = await session("libread");
    await readonly.goto(cfg.origin + "/business/sf_loan");
    await visible(
      readonly.locator(".v-card-title").filter({ hasText: defs.loan.label }),
    );
    await absent(
      readonly.getByRole("button", {
        name: "新增" + defs.loan.label,
        exact: true,
      }),
    );
    await absent(
      readonly.getByRole("button", { name: label("approve"), exact: true }),
    );
    mark("readonly reader has no mutation controls");
    const none = await session("libnone");
    await none.goto(cfg.origin + "/business/sf_loan");
    await none.waitForURL("**/error-403");
    await none.screenshot({
      path: path.join(cfg.reports, "browser-denied.png"),
      fullPage: true,
    });
    mark("no-access reader cannot enter lending route");
  });
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
