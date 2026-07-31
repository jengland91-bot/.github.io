# AGENTS.md

## Cursor Cloud specific instructions

This repository is a single static, dependency-free web page (`index.html`) — a
"link-in-bio" / profile links page intended to be published via GitHub Pages.
There is no package manager, build step, test suite, or lint config.

### Running it in development

Serve the repository root with any static file server and open the page. The
simplest zero-dependency option (Python is preinstalled) is:

```
python3 -m http.server 8000
```

Then open `http://localhost:8000/`. Editing `index.html` and reloading the
browser is the full dev loop; there is nothing to compile or bundle.

### Notes

- No dependencies to install, so the startup update script is intentionally a
  no-op.
- There are no automated tests, lint, or build commands. Verification is manual:
  load the page and confirm the profile section and link cards render and that
  the link cards are clickable (each opens its `href` in a new tab).
