const fs = require("fs"),
  path = require("path");
(async () => {
  const cfg = JSON.parse(fs.readFileSync(0, "utf8"));
  const { withBrowser } = require(cfg.support);
  const defs = Object.fromEntries(cfg.entities.map((e) => [e.name, e]));
  const label = (name) =>
    defs.loan.workflow.transitions.find((a) => a.name === name).label;
  const state = (name) => defs.loan.workflow.state_labels?.[name] || name;
  await withBrowser(cfg, async ({ session, visible, absent, mark }) => {
    const admin = await session("sfadmin");
    await admin.goto(cfg.origin + "/business/sf_book");
    await admin
      .getByRole("button", { name: "新增" + defs.book.label, exact: true })
      .click();
    let dialog = admin.getByRole("dialog");
    await dialog.getByTestId("field-code").locator("input").fill(cfg.book.code);
    await dialog.getByTestId("field-name").locator("input").fill(cfg.book.name);
    await dialog
      .getByTestId("field-stock")
      .locator("input")
      .fill(String(cfg.book.stock));
    await dialog.getByRole("button", { name: "保存", exact: true }).click();
    await visible(
      admin.getByRole("cell", { name: cfg.book.code, exact: true }),
    );
    mark("admin creates book with stock two");
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
    admin.on("dialog", (d) => d.accept());
    await row
      .getByRole("button", { name: label("approve"), exact: true })
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
