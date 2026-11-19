"""Public routes and cross-language content contracts."""
SOLUTION_SLUGS = ('trade', 'technology', 'logistics', 'government', 'sourcing', 'furniture', 'applications')
PAGES = ('', 'about', 'solutions', 'markets', 'partners', 'contact', 'privacy') + tuple(
    'solutions/' + slug for slug in SOLUTION_SLUGS
) + ('global-network', 'corporate-profile')


def validate_content(content):
    reference = content['en']
    for language, locale in content.items():
        if locale.keys() != reference.keys():
            raise ValueError(f'{language}: translation keys differ from English')
        if locale['categories'].keys() != reference['categories'].keys():
            raise ValueError(f'{language}: category IDs differ from English')
        slugs = [s['slug'] for s in locale['solutions']]
        if len(slugs) != len(set(slugs)) or set(slugs) != set(SOLUTION_SLUGS):
            raise ValueError(f'{language}: solution routes do not match the public route registry')
        for solution in locale['solutions']:
            if str(solution['category']) not in locale['categories']:
                raise ValueError(f'{language}: unknown category for {solution["slug"]}')
        countries = [c['id'] for c in locale['countries']]
        if len(countries) != len(set(countries)) or countries != [c['id'] for c in reference['countries']]:
            raise ValueError(f'{language}: country IDs differ from English')
