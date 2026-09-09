import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const node = process.execPath;
const mock = spawn(node, [path.join(root, "e2e", "mock-supabase-server.mjs")], { cwd: root, stdio: "inherit" });
const npm = process.platform === "win32" ? "npm.cmd" : "npm";
const next = spawn(npm, ["run", "dev", "-w", "apps/web", "--", "--port", "3000"], {
  cwd: root,
  stdio: "inherit",
  shell: process.platform === "win32",
  env: {
    ...process.env,
    NEXT_PUBLIC_SUPABASE_URL: "http://127.0.0.1:54321",
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: "e2e-publishable-key",
  },
});

function stop() {
  next.kill();
  mock.kill();
}
process.on("SIGINT", stop);
process.on("SIGTERM", stop);
process.on("exit", stop);
next.on("exit", (code) => process.exit(code ?? 1));
