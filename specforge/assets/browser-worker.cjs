const fs = require("fs"),
  path = require("path"),
  { spawn } = require("child_process");
const root = process.argv[2],
  active = new Set();
const timer = setInterval(() => {
  for (const name of fs.readdirSync(root)) {
    const folder = path.join(root, name),
      request = path.join(folder, "request.json");
    if (!fs.existsSync(request) || active.has(folder)) continue;
    active.add(folder);
    let cfg;
    try {
      cfg = JSON.parse(fs.readFileSync(request, "utf8"));
    } catch {
      active.delete(folder);
      continue;
    }
    const child = spawn(process.execPath, [cfg.script], {
      windowsHide: true,
      stdio: ["pipe", "pipe", "pipe"],
    });
    let stdout = "",
      stderr = "";
    child.stdout.on("data", (b) => (stdout += b.toString()));
    child.stderr.on("data", (b) => (stderr += b.toString()));
    function finish(code) {
      if (!fs.existsSync(folder)) return;
      const tmp = path.join(folder, "completed.tmp");
      fs.writeFileSync(
        tmp,
        JSON.stringify({ returncode: code, stdout, stderr }),
      );
      fs.renameSync(tmp, path.join(folder, "completed.json"));
    }
    child.on("error", (e) => {
      stderr += String(e);
      finish(1);
    });
    child.on("close", (code) => finish(code ?? 1));
    child.stdin.end(JSON.stringify(cfg.settings));
  }
}, 300);
