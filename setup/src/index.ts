#!/usr/bin/env bun
import { spawnSync } from "child_process";
import { existsSync, mkdirSync, createWriteStream } from "fs";
import { homedir, platform } from "os";
import { join } from "path";
import * as readline from "readline";
import * as https from "https";
import * as fs from "fs";

// ── ANSI helpers ──────────────────────────────────────────────────────────────

const c = {
  reset:  "\x1b[0m",
  bold:   "\x1b[1m",
  dim:    "\x1b[2m",
  green:  "\x1b[32m",
  yellow: "\x1b[33m",
  red:    "\x1b[31m",
  cyan:   "\x1b[36m",
  white:  "\x1b[37m",
};

const ok   = (s: string) => `${c.green}✓${c.reset} ${s}`;
const warn = (s: string) => `${c.yellow}!${c.reset} ${s}`;
const err  = (s: string) => `${c.red}✗${c.reset} ${s}`;
const bold = (s: string) => `${c.bold}${s}${c.reset}`;
const dim  = (s: string) => `${c.dim}${s}${c.reset}`;
const cyan = (s: string) => `${c.cyan}${s}${c.reset}`;

const IS_WIN   = platform() === "win32";
const IS_MAC   = platform() === "darwin";
const IS_LINUX = platform() === "linux";

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });

function ask(question: string): Promise<string> {
  return new Promise(resolve => rl.question(question, resolve));
}

function run(cmd: string, args: string[], cwd?: string): boolean {
  const result = spawnSync(cmd, args, { cwd, stdio: "inherit", shell: IS_WIN });
  return result.status === 0;
}

function check(cmd: string, args: string[] = ["--version"]): string | null {
  const result = spawnSync(cmd, args, { stdio: "pipe", shell: IS_WIN });
  if (result.status === 0) return result.stdout.toString().trim().split("\n")[0];
  return null;
}

function openUrl(url: string) {
  const cmd = IS_WIN ? "start" : IS_MAC ? "open" : "xdg-open";
  spawnSync(cmd, [url], { shell: true, stdio: "ignore" });
}

function downloadFile(url: string, dest: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const file = createWriteStream(dest);
    const request = (u: string) => {
      https.get(u, res => {
        if (res.statusCode === 301 || res.statusCode === 302) {
          request(res.headers.location!);
          return;
        }
        res.pipe(file);
        file.on("finish", () => { file.close(); resolve(); });
      }).on("error", reject);
    };
    request(url);
  });
}

// ── Dependency installers ─────────────────────────────────────────────────────

async function installGit(): Promise<boolean> {
  console.log(`  ${dim("Installing git...")}`);

  if (IS_WIN) {
    const tmp = join(homedir(), "AppData", "Local", "Temp", "git-installer.exe");
    console.log(`  ${dim("Downloading Git for Windows...")}`);
    await downloadFile(
      "https://github.com/git-for-windows/git/releases/download/v2.45.1.windows.1/Git-2.45.1-64-bit.exe",
      tmp
    );
    return run(tmp, ["/VERYSILENT", "/NORESTART", "/NOCANCEL", "/SP-", "/CLOSEAPPLICATIONS", "/RESTARTAPPLICATIONS", "/COMPONENTS=icons,ext\\reg\\shellhere,assoc,assoc_sh"]);
  }

  if (IS_MAC) {
    console.log(`  ${dim("Triggering Xcode Command Line Tools install...")}`);
    console.log(`  ${dim("A system dialog will appear — click Install.")}`);
    run("xcode-select", ["--install"]);
    console.log();
    await ask("  Press Enter once the installation completes... ");
    return !!check("git");
  }

  if (IS_LINUX) {
    // Detect package manager
    if (check("apt-get", ["--version"])) {
      return run("sudo", ["apt-get", "install", "-y", "git"]);
    } else if (check("dnf", ["--version"])) {
      return run("sudo", ["dnf", "install", "-y", "git"]);
    } else if (check("pacman", ["--version"])) {
      return run("sudo", ["pacman", "-S", "--noconfirm", "git"]);
    }
  }

  return false;
}

async function installPython(): Promise<boolean> {
  console.log(`  ${dim("Installing Python...")}`);

  if (IS_WIN) {
    const tmp = join(homedir(), "AppData", "Local", "Temp", "python-installer.exe");
    console.log(`  ${dim("Downloading Python for Windows...")}`);
    await downloadFile(
      "https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe",
      tmp
    );
    return run(tmp, ["/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_test=0"]);
  }

  if (IS_MAC) {
    if (check("brew")) {
      return run("brew", ["install", "python3"]);
    }
    // No Homebrew — open Python download page
    console.log(`  ${dim("Opening Python download page...")}`);
    openUrl("https://www.python.org/downloads/macos/");
    console.log();
    await ask("  Press Enter once Python is installed... ");
    return !!(check("python3") || check("python"));
  }

  if (IS_LINUX) {
    if (check("apt-get", ["--version"])) {
      return run("sudo", ["apt-get", "install", "-y", "python3", "python3-pip"]);
    } else if (check("dnf", ["--version"])) {
      return run("sudo", ["dnf", "install", "-y", "python3", "python3-pip"]);
    } else if (check("pacman", ["--version"])) {
      return run("sudo", ["pacman", "-S", "--noconfirm", "python", "python-pip"]);
    }
  }

  return false;
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  console.clear();
  console.log();
  console.log(`${c.bold}${c.white}  Cortex Setup${c.reset}`);
  console.log(`  ${dim("Private AI-scribed record-keeping — cordfuse/cortex")}`);
  console.log();
  console.log("  This wizard will get you running in a few minutes.");
  console.log();

  // ── Step 1: Prerequisites ──────────────────────────────────────────────────

  console.log(bold("── Step 1: Prerequisites ──────────────────────────────────────"));
  console.log();

  // git
  let gitVersion = check("git");
  if (!gitVersion) {
    console.log(warn("git not found — installing..."));
    const installed = await installGit();
    gitVersion = check("git");
    if (!installed || !gitVersion) {
      console.log(err("git installation failed."));
      console.log("  Please install git manually from https://git-scm.com and re-run.");
      process.exit(1);
    }
  }
  console.log(ok(`git — ${dim(gitVersion)}`));

  // python
  let pythonCmd = check("python3") ? "python3" : check("python") ? "python" : null;
  if (!pythonCmd) {
    console.log(warn("Python not found — installing..."));
    const installed = await installPython();
    pythonCmd = check("python3") ? "python3" : check("python") ? "python" : null;
    if (!installed || !pythonCmd) {
      console.log(err("Python installation failed."));
      console.log("  Please install Python 3 manually from https://python.org and re-run.");
      process.exit(1);
    }
  }
  const pyVersion = check(pythonCmd) ?? "";
  console.log(ok(`Python — ${dim(pyVersion)}`));

  // AI agent CLI
  const agents = [
    { cmd: "claude",   label: "Claude Code" },
    { cmd: "gemini",   label: "Gemini CLI"  },
    { cmd: "opencode", label: "OpenCode"    },
  ];
  const foundAgents = agents.filter(a => check(a.cmd, ["--version"]) || check(a.cmd, ["--help"]));

  if (foundAgents.length === 0) {
    console.log(warn("No AI agent CLI found."));
    console.log("  Recommended: Claude Code — https://claude.ai/download");
    console.log();
    const cont = await ask("  Continue anyway? [y/N] ");
    if (cont.toLowerCase() !== "y") process.exit(0);
  } else {
    for (const a of foundAgents) console.log(ok(a.label));
  }

  console.log();

  // ── Step 2: Create your repo ───────────────────────────────────────────────

  console.log(bold("── Step 2: Create your Cortex repo ───────────────────────────"));
  console.log();
  console.log("  Your records live in a private GitHub repo you own.");
  console.log("  We'll open the template now — click " + bold("Use this template") + ".");
  console.log();

  const openBrowser = await ask("  Open GitHub in your browser? [Y/n] ");
  if (openBrowser.toLowerCase() !== "n") {
    openUrl("https://github.com/cordfuse/cortex/generate");
    console.log();
    console.log(dim("  → Name your repo anything (e.g. my-cortex)"));
    console.log(dim("  → Set it to Private"));
    console.log(dim("  → Click Create repository"));
    console.log();
  }

  const repoUrl = await ask("  Your repo URL (e.g. https://github.com/you/my-cortex): ");
  if (!repoUrl.trim()) {
    console.log(err("No URL entered. Exiting."));
    process.exit(1);
  }

  console.log();

  // ── Step 3: Clone ──────────────────────────────────────────────────────────

  console.log(bold("── Step 3: Clone your repo ────────────────────────────────────"));
  console.log();

  const defaultDir = join(homedir(), "cortex");
  const cloneDir = await ask(`  Where to clone? [${defaultDir}] `);
  const targetDir = cloneDir.trim() || defaultDir;

  if (existsSync(targetDir)) {
    console.log(warn(`${targetDir} already exists — skipping clone.`));
  } else {
    console.log(`  Cloning into ${cyan(targetDir)}...`);
    console.log();
    const cloned = run("git", ["clone", repoUrl.trim(), targetDir]);
    if (!cloned) {
      console.log();
      console.log(err("Clone failed. Check the URL and your GitHub access, then re-run."));
      process.exit(1);
    }
  }

  console.log();
  console.log(ok("Repo ready."));
  console.log();

  // ── Step 4: Python deps ────────────────────────────────────────────────────

  console.log(bold("── Step 4: Install Python dependencies ────────────────────────"));
  console.log();

  const pipCmd = check("pip3") ? "pip3" : "pip";
  const deps = [
    "google-auth", "google-auth-oauthlib", "google-api-python-client",
    "msal", "requests", "cryptography"
  ];
  console.log(`  Installing: ${dim(deps.join(", "))}`);
  console.log();
  run(pipCmd, ["install", "--quiet", "--user", ...deps]);
  console.log(ok("Dependencies installed."));
  console.log();

  // ── Step 5: Google integration ─────────────────────────────────────────────

  console.log(bold("── Step 5: Google integration (optional) ──────────────────────"));
  console.log();
  console.log("  Connect Calendar, Gmail, Drive, Tasks, and Contacts.");
  console.log(`  ${dim("Setup guide: docs/setup-google.md in your repo")}`);
  console.log();

  const setupGoogle = await ask("  Set up Google integration now? [y/N] ");
  if (setupGoogle.toLowerCase() === "y") {
    console.log();
    run(pythonCmd, ["scripts/integrations/google.py", "auth"], targetDir);
  } else {
    console.log(dim("  Skipped. Run when ready: python scripts/integrations/google.py auth"));
  }

  console.log();

  // ── Step 6: Microsoft 365 ─────────────────────────────────────────────────

  console.log(bold("── Step 6: Microsoft 365 integration (optional) ───────────────"));
  console.log();
  console.log("  Connect Outlook, Calendar, OneDrive, Teams, SharePoint, To Do, Planner, OneNote.");
  console.log(`  ${dim("Setup guide: docs/setup-microsoft.md in your repo")}`);
  console.log();

  const setupMsft = await ask("  Set up Microsoft 365 integration now? [y/N] ");
  if (setupMsft.toLowerCase() === "y") {
    console.log();
    run(pythonCmd, ["scripts/integrations/microsoft.py", "auth"], targetDir);
  } else {
    console.log(dim("  Skipped. Run when ready: python scripts/integrations/microsoft.py auth"));
  }

  console.log();

  // ── Done ───────────────────────────────────────────────────────────────────

  console.log(bold("── Done ───────────────────────────────────────────────────────"));
  console.log();
  console.log(`  ${c.green}${c.bold}Your Cortex is ready.${c.reset}`);
  console.log();
  console.log("  To start your first session:");
  console.log();
  console.log(`    ${cyan(`cd ${targetDir}`)}`);

  if (foundAgents.length > 0) {
    console.log(`    ${cyan(foundAgents[0].cmd)}`);
  } else {
    console.log(`    ${cyan("claude")}   ${dim("# or: gemini / opencode / qwen")}`);
  }

  console.log();
  console.log("  Say hello. The scribe takes it from there.");
  console.log();

  rl.close();
}

main().catch(e => {
  console.error(err(String(e)));
  process.exit(1);
});
