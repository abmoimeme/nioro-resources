# Updating niororesources.com

This branch prepares the expanded bilingual corporate website for the existing repository at https://github.com/abmoimeme/nioro-resources . The existing CNAME is preserved as `niororesources.com`.

## Review and release

Review the `website/global-network-refresh` branch before merging. Check the repository Settings → Pages configuration. The checked-in root output is compatible with publishing from `main` and `/ (root)`. Repository settings and DNS have not been changed or independently confirmed by this preparation.

If GitHub Pages is already configured to publish `main` at the root, merging this branch should trigger its deployment. Otherwise, connect the actual host before expecting an update. A Git push alone is not proof that the live domain changed.

## Editing

Edit content in `src/content.py`, styling in `src/styles.css`, interactions in `src/app.js`, and templates in `build.py`. Then run:

```sh
python3 build.py
python3 check.py
node --check src/app.js
python3 publish-root.py
```

Commit source and refreshed root output together. The GitHub check rebuilds the website and fails if committed output is stale. The `.nojekyll` file keeps this site static.

The previous company website and app catalog are retained under `/legacy/`. Its original app links, support email and privacy content remain available. The development department links to that catalog. The old `/privacy.html` URL redirects to the updated corporate privacy page. The former Markets URLs remain available.

Public canonical URLs and the sitemap use https://niororesources.com and indexing is enabled. The separate private ChatGPT Site is not changed by this GitHub branch.

Forms continue to prepare email drafts to partner@niororesources.com; no direct submission provider is connected. The presence of a form or successful build does not confirm mailbox delivery.
