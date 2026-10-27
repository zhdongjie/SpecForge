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
  await withBrowser(cfg, async ({ session, visible, absent, mark, assert }) => {
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
    await row
      .getByRole("button", { name: actionLabel("approve"), exact: true })
      .click();
    await admin
      .getByRole("dialog")
      .getByRole("button", { name: "确认", exact: true })
      .click();
    await visible(
      row.getByRole("cell", { name: stateLabel("APPROVED"), exact: true }),
    );
    await row
      .getByRole("button", { name: actionLabel("return_device"), exact: true })
      .click();
    await admin
      .getByRole("dialog")
      .getByRole("button", { name: "确认", exact: true })
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
    await admin.goto(cfg.origin + "/business/sf_device");
    const deviceRow = admin
      .getByRole("row")
      .filter({ hasText: cfg.device.code });
    await deviceRow.getByRole("button", { name: "详情", exact: true }).click();
    await visible(
      admin.getByRole("dialog").getByText(cfg.device.name, { exact: true }),
    );
    await admin
      .getByRole("dialog")
      .getByRole("button", { name: "关闭", exact: true })
      .click();
    await deviceRow.getByRole("button", { name: "删除", exact: true }).click();
    await admin
      .getByRole("dialog")
      .getByRole("button", { name: "取消", exact: true })
      .click();
    await visible(deviceRow);
    mark("generic details and delete cancellation preserve the record");
    await admin.locator(".v-data-table-footer .v-select").click();
    await visible(admin.getByRole("option", { name: "100", exact: true }));
    await absent(admin.getByRole("option", { name: "200", exact: true }));
    const pageResponse = admin.waitForResponse((response) => {
      const url = new URL(response.url());
      return (
        url.pathname.endsWith("/page") &&
        url.searchParams.get("pageSize") === "10"
      );
    });
    await admin.getByRole("option", { name: "10", exact: true }).click();
    assert.equal((await pageResponse).status(), 200);
    mark(
      "template page-size selection respects backend maximum and requests ten rows",
    );
    await admin.setViewportSize({ width: 390, height: 844 });
    await absent(admin.getByText("排序方式", { exact: true }));
    await admin
      .getByRole("button", { name: "新增" + defs.device.label, exact: true })
      .click();
    await visible(
      admin
        .getByRole("dialog")
        .getByRole("button", { name: "保存", exact: true }),
    );
    assert.ok(
      await admin.evaluate(
        () => document.querySelector(".v-dialog--fullscreen") !== null,
      ),
    );
    assert.ok(
      await admin.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth + 1,
      ),
    );
    await admin.screenshot({
      path: path.join(cfg.reports, "browser-generic-editor-mobile.png"),
      fullPage: true,
    });
    await admin
      .getByRole("dialog")
      .getByRole("button", { name: "取消", exact: true })
      .click();
    mark("generic mobile form is fullscreen without horizontal overflow");
  });
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
