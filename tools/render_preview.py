#!/usr/bin/env python3
"""Render a local static preview for file/browser checks.

This is not a replacement for GitHub Pages. It exists so the homepage can be
previewed locally without installing Ruby or Jekyll.
"""

from __future__ import annotations

import html
import pathlib
import shutil

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "_preview"


def esc(value: object) -> str:
    return html.escape(str(value or ""))


def link_attrs(url: object) -> str:
    value = str(url or "")
    if value.startswith("mailto:") or value.startswith("#"):
        return ""
    return ' target="_blank" rel="noreferrer"'


def render_links(items: list[dict] | None) -> str:
    return "".join(
        f'<a href="{esc(link.get("url"))}"{link_attrs(link.get("url"))}>{esc(link.get("label"))}</a>'
        for link in (items or [])
    )


def render_module(module: dict, number: int) -> str:
    module_id = esc(module["id"])
    kind = module.get("type")
    heading = (
        f'<div class="module-heading"><p>{number:02d}</p>'
        f'<h2 id="{module_id}-title">{esc(module["title"])}</h2>'
        + (f'<span>{esc(module.get("intro"))}</span>' if module.get("intro") else "")
        + "</div>"
    )

    if kind == "prose":
        content = '<div class="prose">' + "".join(
            f"<p>{esc(paragraph)}</p>" for paragraph in module.get("body", [])
        ) + "</div>"
    elif kind == "timeline":
        items = []
        for item in module.get("items", []):
            details = ""
            if item.get("details"):
                details = '<ul class="detail-list">' + "".join(
                    f"<li>{esc(detail)}</li>" for detail in item["details"]
                ) + "</ul>"
            meta = ""
            if item.get("meta") or item.get("location"):
                joiner = " · " if item.get("meta") and item.get("location") else ""
                meta = f'<p>{esc(item.get("meta"))}{joiner}{esc(item.get("location"))}</p>'
            items.append(
                '<article class="timeline-item"><div>'
                + (f'<span class="period">{esc(item.get("date"))}</span>' if item.get("date") else "")
                + f'<h3>{esc(item.get("title"))}</h3></div>{meta}{details}</article>'
            )
        content = '<div class="timeline">' + "".join(items) + "</div>"
    elif kind == "cards":
        if module.get("items"):
            cards = []
            for item in module.get("items", []):
                meta = ""
                if item.get("date") or item.get("meta"):
                    joiner = " · " if item.get("date") and item.get("meta") else ""
                    meta = f'<p class="meta">{esc(item.get("date"))}{joiner}{esc(item.get("meta"))}</p>'
                cards.append(
                    '<article class="paper-card">'
                    + meta
                    + f'<h3>{esc(item.get("title"))}</h3>'
                    + (f'<p>{esc(item.get("location"))}</p>' if item.get("location") else "")
                    + (f'<p>{esc(item.get("summary"))}</p>' if item.get("summary") else "")
                    + (
                        f'<div class="item-actions">{render_links(item.get("links"))}</div>'
                        if item.get("links")
                        else ""
                    )
                    + "</article>"
                )
            content = '<div class="item-list">' + "".join(cards) + "</div>"
        else:
            content = f'<div class="prose"><p><em>{esc(module.get("empty", "More soon."))}</em></p></div>'
    elif kind == "compact":
        content = '<div class="compact-list">' + "".join(
            '<article class="compact-item">'
            + (f'<span>{esc(item.get("date"))}</span>' if item.get("date") else "")
            + f'<strong>{esc(item.get("title"))}</strong>'
            + (f'<p>{esc(item.get("summary"))}</p>' if item.get("summary") else "")
            + "</article>"
            for item in module.get("items", [])
        ) + "</div>"
    elif kind == "contact":
        content = (
            f'<div class="contact-card"><h3>{esc(module.get("intro"))}</h3>'
            f'<div class="contact-links">{render_links(module.get("links"))}</div></div>'
        )
    else:
        content = ""

    return (
        f'<section class="module module-{esc(kind)}" id="{module_id}" aria-labelledby="{module_id}-title">'
        f'{heading}<div class="module-content">{content}</div></section>'
    )


def main() -> None:
    profile = yaml.safe_load((ROOT / "_data/profile.yml").read_text())
    modules = [
        module
        for module in yaml.safe_load((ROOT / "_data/modules.yml").read_text())
        if module.get("enabled")
    ]

    shutil.rmtree(OUT, ignore_errors=True)
    (OUT / "assets/css").mkdir(parents=True)
    shutil.copy(ROOT / "assets/css/style.css", OUT / "assets/css/style.css")
    shutil.copy(ROOT / "script.js", OUT / "script.js")

    nav = "".join(
        f'<a href="#{esc(module["id"])}">{esc(module["title"])}</a>'
        for module in modules
        if module.get("nav")
    )
    module_html = "".join(render_module(module, index + 1) for index, module in enumerate(modules))
    profile_links = render_links(profile.get("links"))
    hero_links = render_links(profile.get("links", [])[:3])

    html_doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Local Preview - {esc(profile.get("name"))}</title>
    <script>
      (function () {{
        try {{
          var storedTheme = localStorage.getItem("theme");
          var systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
          document.documentElement.dataset.theme = storedTheme || (systemDark ? "dark" : "light");
        }} catch (error) {{
          document.documentElement.dataset.theme = "light";
        }}
      }})();
    </script>
    <link rel="stylesheet" href="assets/css/style.css">
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to main content</a>
    <div class="site-shell">
      <aside class="profile-panel" aria-label="Profile">
        <div class="profile-card">
          <div class="avatar" aria-hidden="true"><span>{esc(profile.get("avatar_initials"))}</span></div>
          <p class="name">{esc(profile.get("name"))}</p>
          <p class="role">{esc(profile.get("role"))}</p>
          <p class="summary">{esc(profile.get("summary"))}</p>
          <div class="profile-links" aria-label="Profile links">{profile_links}</div>
        </div>
        <nav class="side-nav" aria-label="Page navigation">{nav}</nav>
      </aside>
      <div class="content-panel">
        <header class="topbar">
          <a class="brand" href="#top" aria-label="Back to top">{esc(profile.get("name"))}</a>
          <button class="menu-button" type="button" aria-expanded="false" aria-controls="mobile-nav">
            <span></span><span></span><span></span><span class="sr-only">Open navigation</span>
          </button>
          <nav class="top-nav" aria-label="Top navigation">{nav}</nav>
          <button class="theme-toggle" type="button" aria-label="Switch to dark mode" aria-pressed="false">
            <span class="theme-icon theme-icon-moon" aria-hidden="true"></span>
            <span class="theme-icon theme-icon-sun" aria-hidden="true"></span>
          </button>
        </header>
        <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile navigation">{nav}</nav>
        <main id="main">
          <section class="hero" id="top" aria-labelledby="intro-title">
            <div class="hero-copy">
              <h1 id="intro-title">Hi, I’m <span>{esc(profile.get("short_name"))}</span>.</h1>
              <p>{esc(profile.get("summary"))}</p>
              <div class="hero-links" aria-label="Primary links">{hero_links}</div>
            </div>
          </section>
          {module_html}
        </main>
      </div>
    </div>
    <script src="script.js"></script>
  </body>
</html>
"""
    (OUT / "index.html").write_text(html_doc)
    print(OUT / "index.html")


if __name__ == "__main__":
    main()
