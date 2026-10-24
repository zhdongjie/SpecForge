const fs = require("fs"),
  path = require("path"),
  assert = require("node:assert/strict");
async function withBrowser(cfg, scenario) {
  const { chromium } = require(cfg.module);
  const browser = await chromium.launch({
    headless: true,
    ...(cfg.executable ? { executablePath: cfg.executable } : {}),
  });
  const checks = [];
  async function visible(locator) {
    await locator.waitFor({ state: "visible" });
  }
  async function absent(locator) {
    await locator.waitFor({ state: "hidden" });
    assert.equal(await locator.count(), 0);
  }
  async function session(name) {
    const context = await browser.newContext({
      locale: "zh-CN",
      viewport: { width: 1440, height: 1000 },
    });
    const page = await context.newPage();
    page.setDefaultTimeout(15000);
    await page.goto(cfg.origin + "/authorize/login");
    await page.getByLabel("用户名", { exact: true }).fill(name);
    await page.getByLabel("密码", { exact: true }).fill(cfg.password);
    await page.getByRole("button", { name: "登录", exact: true }).click();
    await page.waitForURL("**/workbench");
    return page;
  }
  try {
    await scenario({
      session,
      visible,
      absent,
      mark: (label) => checks.push(label),
      assert,
    });
    fs.writeFileSync(
      path.join(cfg.reports, "browser.json"),
      JSON.stringify({ status: "PASS", checks }, null, 2),
    );
  } catch (error) {
    fs.writeFileSync(
      path.join(cfg.reports, "browser.json"),
      JSON.stringify({ status: "FAIL", checks, error: String(error) }, null, 2),
    );
    let i = 0;
    for (const context of browser.contexts())
      for (const page of context.pages())
        await page
          .screenshot({
            path: path.join(cfg.reports, "browser-failure-" + i++ + ".png"),
            fullPage: true,
          })
          .catch(() => {});
    throw error;
  } finally {
    await browser.close();
  }
}
module.exports = { withBrowser };
