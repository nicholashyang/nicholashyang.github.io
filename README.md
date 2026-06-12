# Hao Yang's Homepage

Source for `nicholashyang.github.io`, built with GitHub Pages and Jekyll.

The homepage is intentionally data-driven: most content changes should happen in YAML files, not in the HTML template.

## Edit Content

- `_data/profile.yml`: name, role, summary, email, location, avatar initials, and profile links
- `_data/modules.yml`: homepage modules, module order, module visibility, and module items
- `assets/css/style.css`: visual design
- `_includes/module.html`: shared renderer for module types
- `index.html`: page shell; usually you should not need to edit it

## Add, Remove, Or Reorder Modules

Open `_data/modules.yml`.

To hide a module:

```yaml
enabled: false
```

To remove a module, delete its whole block from `_data/modules.yml`.

To reorder modules, move the whole block up or down in `_data/modules.yml`.

To add a module, copy an existing block and change:

```yaml
- id: new-section
  title: New Section
  nav: true
  enabled: true
  type: cards
  intro: Short section description.
  items:
    - title: Example item
      date: 2026
      meta: Optional metadata
      summary: Optional one-sentence summary
      links:
        - label: Link
          url: https://example.com
```

Supported module `type` values:

- `prose`: paragraphs in `body`
- `timeline`: dated entries in `items`
- `cards`: card-style entries in `items`
- `compact`: compact award/list entries in `items`
- `contact`: contact callout with `links`

## Sync Publications From INSPIRE

The Publications module reads `_data/publications.yml`.

To refresh it locally from the INSPIRE author profile linked in `_data/profile.yml`:

```bash
python3 tools/fetch_inspire_publications.py
```

The repository also includes `.github/workflows/sync-publications.yml`, which can refresh publications automatically:

- weekly on Monday at 03:17 UTC
- manually from GitHub Actions via `workflow_dispatch`

The sync script uses the INSPIRE literature API, not HTML scraping.

## Local Preview

The repository root `index.html` is a Jekyll/Liquid template. Do not open it directly with `file://`; the browser cannot render `_data`, `_includes`, or Liquid tags.

Without Ruby/Jekyll, generate a static local preview:

```bash
python3 tools/render_preview.py
```

Then open `_preview/index.html`.

With Ruby/Jekyll installed, preview the real GitHub Pages render:

```bash
bundle exec jekyll serve
```

GitHub Pages renders the Liquid template from the `main` branch.
