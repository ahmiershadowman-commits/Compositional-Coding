# Environment & Toolchain Sense — Agent Prompt

This is a direct instruction from a non-agentic instance of you.
Execute this before anything else in the session. This is not optional.

---

## What you're doing and why

You are about to physically read the environment before forming any assumptions
about it. The failure mode you're preventing: creating parallel environments,
installing duplicate dependencies, assuming toolchain versions, spinning up
infrastructure that already exists.

Do not plan. Do not reason about the task yet. Just read.

---

## Step 1: Project root

Find the project root. Read:

- README.md if present
- Any manifest file present (Cargo.toml, pyproject.toml, package.json, etc.)
- Lockfile if present (Cargo.lock, poetry.lock, package-lock.json, etc.)

Record: language(s), runtime versions pinned, package manager in use.

Do not assume. Read the actual file.

---

## Step 2: Environment inventory

Check what environments actually exist:

- Python: look for `.venv`, `venv`, `env`, `__pypackages__`, any conda envs
- Rust: check toolchain file (`.rust-toolchain`, `.rust-toolchain.toml`)
- Node: check `.nvmrc`, `.node-version`, existing `node_modules`
- Any other runtime: read what's there

If an environment exists, use it. Do not create a new one.
If versions are pinned, respect those pins. Do not upgrade unless explicitly asked.

Record: what exists, what version, where.

---

## Step 3: Installed dependencies

Do not install anything yet. First check what's already installed:

- Python: `pip list` or equivalent in the active env
- Rust: `cargo tree` or check `Cargo.toml [dependencies]`
- Node: read `package.json` dependencies

If what you need is already there, don't reinstall it.
If there's a conflict, surface it — don't resolve it silently.

Record: what's present, what's missing, any version conflicts.

---

## Step 4: Build and test state

Can the project currently build? Can the tests run?
Run the build. Run the tests. Read the output.

Do not assume the project is in a working state. Do not assume it's broken.
Verify.

If something is broken, record it as a found condition — not something to fix
immediately, but something to carry into context.

---

## Step 5: Surface your findings

Before proceeding to any task work, write a short state report:

```
Environment:   [what exists]
Toolchain:     [versions confirmed]
Dependencies:  [present / missing / conflicted]
Build state:   [passing / failing / unknown + reason]
Assumptions I'm NOT making: [list at least two things you verified rather than assumed]
```

This report becomes the first entry in session context.
Only after writing it do you proceed to context rebuilding (`/context-rebuild`).
