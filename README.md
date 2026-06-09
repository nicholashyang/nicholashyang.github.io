# Hao Yang's Homepage

This is the source for `nicholashyang.github.io`, built with GitHub Pages and Jekyll.

## Structure

- `index.html`: Jekyll/Liquid homepage template
- `assets/css/style.css`: page styling
- `_data/*.yml`: education, activities, awards, teaching, and talks data
- `script.js`: mobile navigation and active-section highlighting

## Local Preview

With Ruby/Jekyll installed:

```bash
bundle exec jekyll serve
```

For a quick static layout check without Liquid rendering:

```bash
python3 -m http.server 8000
```

GitHub Pages will render the Liquid template from the `main` branch.
