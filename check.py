#!/usr/bin/env python3
"""Validate every generated document's local links and assets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import re
from src.schema import PAGES
from src.content import CONTENT

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links, self.ids, self.alternates = [], set(), set()
        self.h1, self.lang, self.meta = 0, None, {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if tag == 'h1':
            self.h1 += 1
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                raise ValueError(f'Duplicate ID: {attrs["id"]}')
            self.ids.add(attrs['id'])
        if tag in ('a', 'link', 'script', 'img', 'image'):
            for key in ('href', 'src'):
                if attrs.get(key):
                    self.links.append(attrs[key])
        if tag == 'meta':
            self.meta[attrs.get('name', attrs.get('property'))] = attrs.get('content')
            if attrs.get('http-equiv', '').lower() == 'refresh':
                match = re.search(r'url\s*=\s*(.*)', attrs.get('content', ''), re.I)
                if match:
                    self.links.append(match.group(1).strip(' \"\''))
        if tag == 'link' and attrs.get('rel') == 'alternate':
            self.alternates.add(attrs.get('hreflang'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check(dist=DIST):
    files = sorted(dist.rglob('*.html'))
    require(bool(files), 'No generated pages: run build.py first')
    pages = {}
    for path in files:
        try:
            pages[path] = Page(path.read_text())
        except ValueError as error:
            raise ValueError(f'{path.relative_to(dist)}: {error}') from error

    def check_link(source, reference):
        # External/data/mailto URLs are outside this offline check's scope.
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc:
            return
        resolved = urlsplit(urljoin('/' + source.relative_to(dist).as_posix(), reference))
        target = dist / unquote(resolved.path).lstrip('/')
        require(target.resolve().is_relative_to(dist.resolve()), f'{source}: URL escapes output: {reference}')
        if target.is_dir():
            target /= 'index.html'
        require(target.is_file(), f'{source.relative_to(dist)}: missing target {reference}')
        if resolved.fragment and target in pages:
            require(unquote(resolved.fragment) in pages[target].ids,
                    f'{source.relative_to(dist)}: missing anchor {reference}')

    for path, page in pages.items():
        for reference in page.links:
            check_link(path, reference)
        relative = path.relative_to(dist)
        if relative.parts[0] == 'legacy' or relative.as_posix() == 'privacy.html':
            continue  # Only metadata differs; links above are still validated.
        require(page.lang in CONTENT, f'{relative}: unsupported language')
        require(page.h1 == 1, f'{relative}: expected one H1')
        require(bool(page.meta.get('description')), f'{relative}: missing description')
        require(page.alternates == {'en', 'fr', 'x-default'}, f'{relative}: missing language alternates')
        for forbidden in ('Phoenix', 'niororesources@gmail.com', 'HR43ZR93H2Z1'):
            require(forbidden not in path.read_text(), f'{relative}: excluded text {forbidden}')
    for path in dist.rglob('*.css'):
        css = re.sub(r'/\*.*?\*/', '', path.read_text(), flags=re.S)
        for match in re.finditer(r'''url\(\s*(?:"([^"]*)"|'([^']*)'|([^\s)]*))\s*\)''', css, re.I):
            check_link(path, next(v for v in match.groups() if v is not None))
        for match in re.finditer(r'''@import\s+["']([^"']+)["']''', css, re.I):
            check_link(path, match.group(1))
    for name in ('logo-primary.png', 'logo-reversed.png', 'logo-icon.png'):
        require((dist/'assets'/name).read_bytes() == (ROOT/'src/assets'/name).read_bytes(), f'Logo differs: {name}')
    for language, locale in CONTENT.items():
        expected = {dist/language/page/'index.html' for page in PAGES}
        require(set((dist/language).rglob('index.html')) == expected, f'{language}: unexpected or missing routes')
        require('US / AF / EU / AS' in (dist/language/'index.html').read_text(), f'{language}: map labels')
        network = (dist/language/'global-network/index.html').read_text()
        for country in locale['countries']:
            for attribute in ('data-map-country', 'data-country-panel'):
                require(f'{attribute}="{country["id"]}"' in network, f'{language}: missing {attribute} {country["id"]}')
        for solution in locale['solutions']:
            page = (dist/language/'solutions'/solution['slug']/'index.html').read_text()
            require(f'?category={solution["category"]}#inquiry' in page, f'{language}: incorrect solution category')
    print(f'PASS: {len(pages)} pages; local links, CSS assets, anchors, metadata, routes, logos and inquiry categories.')


if __name__ == '__main__':
    check()
