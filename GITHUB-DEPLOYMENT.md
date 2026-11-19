# Updating niororesources.com

The public site uses GitHub Pages from `main` at `/ (root)` with the custom domain `niororesources.com`. HTTPS enforcement was verified on November 18, 2026. The private ChatGPT preview is a separate deployment and is not updated by this repository.

## Edit, verify and release

Edit `src/content.py`, `src/styles.css`, `src/app.js`, or the templates in `build.py`. Public routes live in `src/schema.py`; category IDs are explicit keys in each locale. Keep existing category IDs stable because links may be bookmarked. Email text is populated from `site.config.json`.

```sh
python3 build.py
python3 check.py
node --check src/app.js
python3 publish-root.py --dry-run
python3 publish-root.py
python3 publish-root.py --check
python3 -m unittest discover -s tests -v
```

Commit the source changes, generated root files, and `generated-files.json` together. `dist/` is disposable, ignored build output. It is never edited or committed.

Review a pull request and its successful checks before merging. Merging to `main` triggers GitHub Pages publishing. Confirm the Pages deployment succeeds and verify the public site. The website check and Pages deployment are separate workflows; this repository does not configure a deployment gate or branch protection.

## Safe output cleanup

The manifest records hashes for generated root files. Publishing removes only retired files previously owned by that manifest, and refuses to delete any retired file that has been edited. Unknown files under `en/`, `fr/`, or `assets/` block publishing for explicit review. `--dry-run` lists planned retirements without writing anything. Do not edit the manifest manually to bypass a warning.

`CNAME`, `.nojekyll`, source, docs, original brand assets, and `legacy/` are preserved. Legacy files are maintained source copied into `dist/` for previews; publishing verifies that copy instead of overwriting the source. The older root `site.js`, `style.css`, and `favicon.svg` remain available pending a review of external usage.

## Compatibility and forms

Keep `/legacy/`, `/legacy/privacy.html`, `/privacy.html`, and former `/en/markets/` and `/fr/markets/` URLs. The applications page links to the legacy app catalog. Existing numeric contact categories retain their meanings.

Forms prepare email drafts to `partner@niororesources.com`. No automatic delivery provider is configured. Follow the README's provider contract if enabling direct submission; never commit credentials.

## Rollback

Revert the cleanup or subsequent change through a reviewed pull request, including source, generated output, and manifest together. For a route retirement, its earlier manifest and generated files are available in Git history. Domain and HTTPS settings are independent of source changes.
