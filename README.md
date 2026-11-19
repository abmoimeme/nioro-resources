Start with **START-HERE.md** for GitHub import and live-site connection instructions.

# Nioro Resources website

A bilingual corporate website using the approved Nioro Resources PNG assets. Includes 16 routes per language, a default English homepage, a 404 page, responsive navigation, inquiry preparation, search metadata and a sitemap.

## Start locally

Requires Python 3.9 or later. No packages, database or build-service account are needed.

```sh
python3 build.py
python3 check.py
python3 -m http.server 4387 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:4387/en/ or http://127.0.0.1:4387/fr/. Stop the server with Control-C. Serve the site over HTTP; opening HTML files directly will not resolve root-relative assets.

## Edit content and branding

- `src/content.py`: English and French text, solution details and market descriptions. Keep both language dictionaries complete.
- `src/styles.css`: shared design, spacing, typography and responsive layouts.
- `src/app.js`: navigation, form validation and email draft handling.
- `build.py`: shared HTML templates and static generation.
- `site.config.json`: destination email, canonical origin, indexing and optional submission endpoint.
- `src/assets/`: original logo PNGs, local Montserrat fonts, map outlines and favicon wrapper.
- `brand-originals/`: all six original approved assets and the supplied ZIP.

After changes, rebuild, run `check.py` and reload your browser. The `dist` directory is regenerated; do not edit it directly. Content editing is file-based; this project does not include a CMS account or dashboard.

## Inquiry handling — current configuration

Recipient: **partner@niororesources.com**, supplied by the owner.

The default form validates required fields and prepares an email. The visitor must click **Open email app**, review the message and send it. The page never says the message was sent. A UTF-8 text download provides a fallback for browsers without an email handler or email clients with URL-length limits. Direct email links are also provided. No test email was sent during development.

The form does not store drafts, send personal data to this site's server, or queue inquiries. Browser validation, a hidden trap field, length limits, a consent field, safe text rendering and clear result states are included. Email delivery and mailbox existence have not been verified.

### Enable direct website submission

1. Configure an HTTPS form provider or your own endpoint to deliver to `partner@niororesources.com`.
2. Set `formEndpoint` in `site.config.json` to that public endpoint. Never place an API secret in this file.
3. The endpoint must accept JSON POST requests, allow this site's origin via CORS, and return a successful HTTP status only when it accepts the inquiry. Fields: `name`, `email`, `organization`, `country`, `website`, `category`, `message`, `consent`, `language`, `source`, `subject`.
4. Enforce server-side validation, request limits, rate limiting and spam protection at the endpoint. The browser honeypot alone is not production spam protection. Do not use a public URL that exposes a private service credential.
5. Update the privacy information with the actual provider and applicable retention practices. Rebuild and redeploy.
6. Test a real accepted inquiry, malformed data, provider rejection, timeout, and mailbox receipt. The UI reports acceptance, not confirmed human review. On uncertain delivery it offers a draft fallback and asks the visitor to check before retrying.

No direct submission provider is currently connected; its live success/error paths and end-to-end delivery remain unverified.

## Pages

Each path exists below `/en/` and `/fr/`:

- Home
- `about/`
- `solutions/`
- `solutions/trade/`
- `solutions/technology/`
- `solutions/logistics/`
- `solutions/government/`
- `global-network/` (interactive six-country network)
- `markets/` (compatible former route; canonical points to Global Network)
- `corporate-profile/`
- `solutions/sourcing/`
- `solutions/furniture/`
- `solutions/applications/`
- `partners/`
- `contact/`
- `privacy/`

Language switching preserves the current page. Solution CTAs select the corresponding contact category. Partners starts with the supplier/partner category selected.

## Deploy to niororesources.com

Upload the contents of `dist/` to a static host supporting directory index pages and a custom `404.html`. Publish the folder contents at the domain root, not under a subdirectory. The `.openai/hosting.json` file identifies the private Sites project; it is not needed for another host.

Before a public-domain launch:

1. Set `origin` to `https://niororesources.com` and `indexable` to `true`, then rebuild. The private review version intentionally uses `noindex` and disallows crawling.
2. Configure the domain's DNS with the chosen host and enable HTTPS. Neither DNS nor the existing domain has been changed by this project.
3. Ensure `.html` directory routes and 404 behavior work. Apply `_headers` where supported, or configure equivalent headers in the host. Avoid a catch-all that returns the homepage with a 200 status for unknown pages.
4. Verify contact delivery, final French copy and public company details. The privacy text is a site-specific draft and needs to reflect actual operational practices and providers.
5. Check mobile Safari, desktop Safari, Chromium and Firefox, keyboard-only navigation, zoom, contrast and a screen reader. Submit `/sitemap.xml` to your search tools after launch.

All pages have language attributes, unique titles, descriptions, canonical URLs, alternate language URLs, social metadata and Organization structured data. The site is fully pre-rendered; content and navigation do not require JavaScript. No analytics or tracking service is configured. Security headers are supplied, but enforcement depends on the host.

## Content boundaries

Founding year 2020 and Arizona headquarters follow the owner's brief. The map shows the **United States, Africa, Europe and Asia**, without Phoenix or other city labels. It shows markets of interest, not actual freight routes or offices. Senegal remains a principal commercial focus. Commercial relationships in France, Italy and Turkey, and sourcing partners in China, follow the owner’s November 18, 2026 update. Other West African markets remain development targets. The new network page distinguishes these roles without implying foreign offices or subsidiaries.

No SAM registration, CAGE code, certifications, client endorsements, contract awards, verified past performance, owned telecom networks or carrier/customs-broker licenses are claimed. No capability-statement download is offered until an approved statement exists. No private tax, banking or residential records are included.

## Assets and licensing

The approved primary, reversed and icon PNGs are byte-for-byte copies from the uploaded ZIP. CSS frames remove excess presentation-sheet whitespace visually; no marks are redrawn or recolored. The favicon is an SVG viewport onto the original icon sheet, embedding the unchanged PNG. The primary logo image is also used for social sharing.

Montserrat is bundled locally under the SIL Open Font License; see `src/assets/FONT-LICENSE.txt`. Font source: Google Fonts, Montserrat family.

The map is derived from Natural Earth 1:110m country boundaries, public-domain geographic data: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson . Labels and connecting lines are illustrative site graphics.

## Validation status

`check.py` checks all generated pages for internal links and anchors, assets, language metadata, one H1 per page, duplicate IDs, map labels and excluded sensitive identifiers. JavaScript syntax is checked with `node --check src/app.js` when Node is available.

Browser checks covered the English homepage and customer form, invalid-field blocking, a valid local email draft with correct recipient, the French homepage at a 390px viewport, and mobile menu navigation to the French partners page. No inquiry was sent. Additional browser/device and direct-submission delivery checks remain launch tasks; no Lighthouse score or formal accessibility conformance is claimed.

## November 18 expansion

The homepage now uses “Global Sourcing. International Trade. Technology Solutions.” The official corporate tagline is retained. Dedicated pages cover international sourcing, furniture and interiors, and the applications, websites and process engineering department. `PROJECT-BRIEF.md` records the expanded scope and publishing boundaries.

The interactive Global Network page highlights the United States, Senegal, France, Italy, Turkey and China. Links and map controls select the corresponding country panel; without JavaScript all panels remain readable. The former markets URLs continue to work. Corporate profiles are available in both languages and have print styling.

Content is organized by locale in `src/content.py` so new languages can reuse the page templates. Adding another language requires its complete content dictionary, language-switch/alternate metadata updates and translated interaction strings in `src/app.js`, followed by route and UI checks. English and French are the released languages.

Expansion verification: all six country selectors were exercised in the browser; clicking the China country outline selected its sourcing-partner panel. Keyboard Enter selected Turkey on the French map at 390px width with no horizontal overflow. The French development-page CTA opened contact category 9. Generated checks passed for all 34 HTML pages and the new service-category links. Direct email delivery remains untested and unconfigured as described above.
