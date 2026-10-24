const fs = require("fs"),
  path = require("path");
(async () => {
  const cfg = JSON.parse(fs.readFileSync(0, "utf8"));
  const { withBrowser } = require(cfg.support);
  const defs = Object.fromEntries(cfg.entities.map((e) => [e.name, e]));
  const actionLabel = (name) =>
    defs.borrow.workflow.transitions.find((a) => a.name === name).label;
  const stateLabel = (state) =>
    defs.borrow.workflow.state_labels?.[state] || state;
  await withBrowser(cfg, async ({ session, visible, absent, mark }) => {
    const admin = await session("sfadmin");
    await admin.goto(cfg.origin + "/business/sf_device");
    await admin
      .getByRole("button", { name: "新增" + defs.device.label, exact: true })
      .click();
    let d = admin.getByRole("dialog");
    await d.getByTestId("field-code").locator("input").fill(cfg.device.code);
    await d.getByTestId("field-name").locator("input").fill(cfg.device.name);
    await d.getByRole("button", { name: "保存", exact: true }).click();
    await visible(
      admin.getByRole("cell", { name: cfg.device.code, exact: true }),
    );
    mark("admin creates device");
    const user = await session("sfa");
    await user.goto(cfg.origin + "/business/sf_borrow");
    await user
      .getByRole("button", { name: "新增" + defs.borrow.label, exact: true })
      .click();
    d = user.getByRole("dialog");
    await d.getByTestId("field-device_id").locator(".v-field").click();
    await user
      .getByRole("option", { name: cfg.device.name, exact: true })
      .click();
    await d.getByTestId("field-reason").locator("input").fill("浏览器流程验收");
    await d.getByRole("button", { name: "保存", exact: true }).click();
    await visible(
      user.getByRole("cell", { name: "浏览器流程验收", exact: true }),
    );
    mark("applicant submits");
    await admin.goto(cfg.origin + "/business/sf_borrow");
    const row = admin.getByRole("row").filter({ hasText: "浏览器流程验收" });
    admin.on("dialog", (d) => d.accept());
    await row
      .getByRole("button", { name: actionLabel("approve"), exact: true })
      .click();
    await visible(
      row.getByRole("cell", { name: stateLabel("APPROVED"), exact: true }),
    );
    await row
      .getByRole("button", { name: actionLabel("return_device"), exact: true })
      .click();
    await visible(
      row.getByRole("cell", { name: stateLabel("RETURNED"), exact: true }),
    );
    mark("admin approves and returns");
    await admin.screenshot({
      path: path.join(cfg.reports, "browser-admin.png"),
      fullPage: true,
    });
    const readonly = await session("sfread");
    await readonly.goto(cfg.origin + "/business/sf_borrow");
    await visible(
      readonly.locator(".v-card-title").filter({ hasText: defs.borrow.label }),
    );
    await absent(
      readonly.getByRole("button", {
        name: "新增" + defs.borrow.label,
        exact: true,
      }),
    );
    await absent(
      readonly.getByRole("button", {
        name: actionLabel("approve"),
        exact: true,
      }),
    );
    mark("readonly cannot mutate");
    const none = await session("sfnone");
    await none.goto(cfg.origin + "/business/sf_borrow");
    await none.waitForURL("**/error-403");
    await none.screenshot({
      path: path.join(cfg.reports, "browser-denied.png"),
      fullPage: true,
    });
    mark("no-access route denied");
  });
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
