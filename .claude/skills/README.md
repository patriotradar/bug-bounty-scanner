# Project skills

Skills vendored into this repo so they load automatically for anyone working in
it (Claude Code discovers `.claude/skills/<name>/SKILL.md`).

## Sources

| Source | Commit | Skills |
| --- | --- | --- |
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui/tree/main/skills) — the skills published at <https://ui.shadcn.com> | `6261bd89f72d794aea491482cc2acfd8dc3d63e2` (2026-08-06) | `shadcn`, `migrate-radix-to-base` |
| [bergside/awesome-design-skills](https://github.com/bergside/awesome-design-skills) | `f631a09b4fcc0166f2e2c1a8c81906ef680c57e8` (2026-06-28) | 67 design-system style skills |

Content is vendored verbatim apart from the one change noted below.

## The two `shadcn` skills

Both upstreams ship a skill named `shadcn`, and skill names must be unique, so
the design-style one was renamed on import:

- **`shadcn/`** — official shadcn/ui skill. Drives the `shadcn` CLI: adding
  components, registries, presets, `components.json`. Declares
  `allowed-tools: Bash(npx shadcn@latest *)` (plus the pnpm/bun equivalents) and
  runs `npx shadcn@latest info --json` to gather project context when it loads.
- **`shadcn-style/`** — from awesome-design-skills; renamed from `shadcn`
  (folder and frontmatter `name`). Pure visual guidance: tokens, palette,
  component styling rules. No tools, no CLI.

## Design skills

The 67 design skills are mutually exclusive aesthetics (`minimal`, `brutalism`,
`glassmorphism`, `editorial`, `terracotta`, …). Each is a folder with:

- `SKILL.md` — agent instructions: tokens, component rules, a11y constraints,
  quality gates
- `DESIGN.md` — human-readable design intent and rationale

Pick one per project or surface and invoke it by name; they are not meant to be
combined. Previews: <https://typeui.sh/design-skills>.

## Updating

Re-copy from upstream and redo the `shadcn` → `shadcn-style` rename:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/shadcn-ui/ui.git
git -C ui sparse-checkout set skills
git clone --depth 1 https://github.com/bergside/awesome-design-skills.git
```

`skills/index.json` from awesome-design-skills is not vendored — its paths are
relative to that repo's layout and do not apply here.
