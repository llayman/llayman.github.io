# llayman.github.io

Personal academic website of Lucas Layman, built with [Hugo](https://gohugo.io/)
and the [HugoBlox](https://hugoblox.com/) `academic-cv` theme (loaded as a Hugo
Module). Content is plain Markdown/YAML; the site is built to static HTML and
deployed to GitHub Pages via GitHub Actions.

This README covers how to **compile, build, and maintain** the site. It is the
working documentation for this repository — not a theme showcase.

---

## Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| **Hugo (extended)** | `0.162.0`+ | Pinned for CI in [`hugoblox.yaml`](hugoblox.yaml) (`build.hugo_version`). Must be the **extended** build (Tailwind/asset pipeline). |
| **Go** | 1.19+ | Required to resolve the theme, which is a Hugo Module (see [`go.mod`](go.mod)). |
| **Node.js** | 22+ | Drives Tailwind CSS v4 and Pagefind search. CI uses Node 22. |
| **pnpm** | 10+ | Package manager (`packageManager` in [`package.json`](package.json)). `npm` works as a fallback. |
| **Python** | 3.x + PyYAML | Only needed for the publication maintenance script ([`scripts/migrate_pubs.py`](scripts/migrate_pubs.py)). |

> Hugo ≥ 0.161 requires the `@tailwindcss/cli` npm package — it is already in
> `package.json`, so a normal install covers it.

---

## Local development

```bash
# 1. Install Node dependencies (Tailwind, Pagefind, Preact)
pnpm install            # or: npm install

# 2. Start the live-reload dev server at http://localhost:1313
pnpm dev                # alias for: hugo server --disableFastRender

# 3. Produce a full production build into ./public
pnpm build              # alias for: hugo --minify && pnpm run pagefind
```

The npm scripts are defined in [`package.json`](package.json):

| Script | Command | Purpose |
| --- | --- | --- |
| `pnpm dev` | `hugo server --disableFastRender` | Local preview with live reload |
| `pnpm build` | `hugo --minify && pnpm run pagefind` | Production build + search index |
| `pnpm pagefind` | `pagefind --site public` | (Re)build the Pagefind search index over `./public` |

For a quick build without the search index, just run `hugo` (or `hugo --minify`).
The HugoBlox CLI equivalents `npx hugoblox dev` / `npx hugoblox build` also work.

### Verifying a clean build

The build should complete with **zero `WARN` lines**. To check:

```bash
hugo 2>&1 | grep -i warn
```

If you see legacy-publication / `doi` / `url_pdf` deprecation warnings, run the
publication migration described below — do **not** silence them with
`ignoreLogs`.

---

## Project structure

```
.
├── config/_default/      # Site configuration (split by concern)
│   ├── hugo.yaml         #   core Hugo settings
│   ├── params.yaml       #   theme params: identity, theme, footer, SEO, etc.
│   ├── menus.yaml        #   top navigation
│   ├── languages.yaml    #   language/i18n
│   └── module.yaml       #   Hugo Module (theme) wiring
├── content/
│   ├── _index.md         # Home page (landing blocks: bio, etc.)
│   └── publications/     # One folder per paper (page bundle): index.md + cite.bib
├── data/authors/me.yaml  # Author profile: name, role, bio, affiliations, links
├── assets/media/         # Avatar and other processed media
├── layouts/_partials/hooks/head-end/   # Custom <head> injections (e.g. custom CSS)
├── static/               # Files copied verbatim (e.g. static/uploads/resume.pdf)
├── publications.bib      # Source bibliography for the publications section
├── scripts/migrate_pubs.py   # Post-import frontmatter migration (see below)
├── hugoblox.yaml         # Pinned Hugo version + deploy target
└── .github/workflows/    # CI: build, deploy, import-publications, upgrade
```

### Common edits

- **Home page** (office address, courses, landing blocks): [`content/_index.md`](content/_index.md)
- **Profile** (name, role, bio, affiliations, social/ORCID links): [`data/authors/me.yaml`](data/authors/me.yaml)
- **Citation style, theme, footer, SEO**: [`config/_default/params.yaml`](config/_default/params.yaml)
- **Custom CSS**: add an `.html` partial under
  [`layouts/_partials/hooks/head-end/`](layouts/_partials/hooks/head-end/) with a
  scoped `<style>` block (any file in that directory is auto-injected into `<head>`).

---

## Maintaining publications

Publications live in `content/publications/<slug>/`, each a page bundle with an
`index.md` (metadata) and `cite.bib` (BibTeX). The source of truth is the
root [`publications.bib`](publications.bib).

### Workflow: updating from BibTeX

1. **Edit** `publications.bib`.
2. **Import** to regenerate the Markdown pages with the `academic` converter
   ([GetRD/academic-file-converter](https://github.com/GetRD/academic-file-converter)):

   ```bash
   # Preview (writes nothing):
   academic import publications.bib content/publications/ --compact --verbose --dry-run

   # Add only NEW entries (skips existing folders):
   academic import publications.bib content/publications/ --compact --verbose

   # Regenerate ALL entries, including edited ones (overwrites index.md):
   academic import publications.bib content/publications/ --compact --verbose --overwrite
   ```

   > `--overwrite` clobbers manual edits to `index.md` (abstracts, links, PDF
   > mirrors) and does **not** delete pages for entries removed from the `.bib` —
   > delete those folders by hand.

3. **Migrate the frontmatter** (required — see next section):

   ```bash
   python3 scripts/migrate_pubs.py            # dry run, prints what would change
   python3 scripts/migrate_pubs.py --write    # apply
   ```

4. **Verify** the build is warning-free: `hugo 2>&1 | grep -i warn` (expect no output).

### Why `scripts/migrate_pubs.py` is needed

The `academic` converter emits the **legacy** publication frontmatter format,
which trips HugoBlox deprecation warnings on every build. HugoBlox tells you to
run `hugoblox migrate publications`, but **that subcommand does not exist** in
the current CLI (only `migrate v0.11.0-authors` and `v0.11.0-events` ship). So
this repo carries its own equivalent.

[`scripts/migrate_pubs.py`](scripts/migrate_pubs.py) rewrites each
`content/publications/*/index.md`:

| Legacy (from `academic import`) | Migrated (structured) |
| --- | --- |
| `publication: '*Journal Name*'` | `publication:`<br>`  name: Journal Name` |
| `doi: 10.x/y` (top level) | `hugoblox:`<br>`  ids:`<br>`    doi: 10.x/y` |
| `url_pdf: https://…` | `links:`<br>`- type: pdf`<br>`  url: https://…` |

It uses a real YAML parser (PyYAML), because some `publication` values wrap
across multiple lines and would be corrupted by line-based `sed` edits. The
script is **idempotent** — running it on already-migrated files reports
`WOULD CHANGE 0 files`. It only touches `index.md`; companion `cite.bib`/PDF
files are left alone.

> The same legacy format is produced by the **Import Publications From Bibtex**
> GitHub Action (`.github/workflows/import-publications.yml`), which opens a PR
> on pushes that change `publications.bib`. Run the migration on that branch
> before merging.

### Hosting a PDF ("PDF mirror")

Because each publication is a page bundle, any file dropped in its folder is
published alongside it. To self-host a PDF, place e.g. `paper.pdf` in
`content/publications/<slug>/` and reference it relatively:

```yaml
links:
- type: pdf
  url: paper.pdf      # served from /publications/<slug>/paper.pdf
```

Only mirror PDFs you have the right to redistribute (author manuscripts, arXiv
preprints).

---

## Building & deploying

Deployment is automated through GitHub Actions (`.github/workflows/`):

| Workflow | Trigger | What it does |
| --- | --- | --- |
| `deploy.yml` | push to `main`, or manual | Builds and deploys to **GitHub Pages** |
| `build.yml` | pull requests to `main`; called by `deploy.yml` | Reusable build job (Node 22 → pnpm install → Hugo extended `--minify` → Pagefind → upload artifact) |
| `import-publications.yml` | push to `main` touching `publications.bib`, or manual | Runs `academic import` and opens a PR with regenerated pages |
| `upgrade.yml` | manual / scheduled | Upgrades HugoBlox modules |

**To publish:** commit and push to `main`. `deploy.yml` reads the deploy target
from [`hugoblox.yaml`](hugoblox.yaml) (`deploy.host: github-pages`), runs the
build, and publishes via `actions/deploy-pages`. The Hugo version used by CI is
pinned in the same file (`build.hugo_version`); bump it there to upgrade the
build toolchain.

To reproduce the CI build locally:

```bash
pnpm install
hugo --minify
pnpm run pagefind
# output is in ./public
```

---

## Upgrading the theme

The theme is a Hugo Module pinned in [`go.mod`](go.mod) / `go.sum`. Update with:

```bash
npx hugoblox upgrade          # HugoBlox-aware module upgrade
# or, directly:
hugo mod get -u ./...
hugo mod tidy
```

After upgrading, run `hugo` and confirm the build is still warning-free before
committing the updated `go.mod`/`go.sum`.

---

## Troubleshooting

- **Deprecation `WARN`s about publications** → run `python3 scripts/migrate_pubs.py --write`.
- **`@tailwindcss/cli` missing** → `pnpm install` (Hugo ≥ 0.161 needs it).
- **Search box returns nothing locally** → the index is only built by
  `pnpm build` / `pnpm pagefind`, not by `hugo server`.
- **Theme/module errors** → ensure Go is installed and run `hugo mod tidy`.
