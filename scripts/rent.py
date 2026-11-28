"""Read the two monthly rental CPI vectors from the regular CPI download."""
from datetime import date
from html import escape
from math import isfinite

# Geography, product, first observation, and dimension members in table 18-10-0004-01.
SERIES = {
    'v41692860': ('Halifax, Nova Scotia', 'Rented accommodation', '1971-01', '8.80'),
    'v41691548': ('Nova Scotia', 'Rent', '1978-09', '7.81'),
}
EXAMPLE_START = '2015-01'


def collect(rent, row):
    vector = row['VECTOR']
    if vector not in SERIES:
        return
    geography, product, _, coordinate = SERIES[vector]
    if (row['GEO'], row['Products and product groups'], row['COORDINATE'],
        row['UOM'], row['SCALAR_FACTOR']) != (geography, product, coordinate, '2002=100', 'units'):
        raise ValueError(f'Unexpected source definition for {vector}')
    if not row['VALUE']:
        return
    month = row['REF_DATE']
    date.fromisoformat(month + '-01')
    index = float(row['VALUE'])
    if not isfinite(index) or index <= 0 or month in rent[vector]:
        raise ValueError(f'Invalid or duplicate {vector} index for {month}')
    rent[vector][month] = index


def validate(rent, edition_end):
    for vector, (_, _, first, _) in SERIES.items():
        months = rent[vector]
        if min(months, default=None) != first or EXAMPLE_START not in months or max(months) != edition_end:
            raise ValueError(f'Truncated rental history for {vector}')


def month_name(month):
    return date.fromisoformat(month + '-01').strftime('%B %Y')


def render_example(page, rent, latest):
    """Keep the default comparison readable before the interactive controls load."""
    validate(rent, latest)
    for vector, months in rent.items():
        a, b = months[EXAMPLE_START], months[latest]
        value = f'{(b / a - 1) * 100:+.1f}%'
        description = f'Index {a:.1f} in {month_name(EXAMPLE_START)} and {b:.1f} in {month_name(latest)}.'
        geo, product = SERIES[vector][3].split('.')
        url = ('https://www150.statcan.gc.ca/t1/tbl1/en/cv!recreate.action?pid=1810000401'
               f'&selectedNodeIds=1D{geo}%2C2D{product}&dimensionLayouts=layout2%2Clayout3%2Clayout2'
               f'&refPeriods={EXAMPLE_START.replace("-", "")}01%2C{latest.replace("-", "")}01&vectorDisplay=true')
        page = page.replace('{{' + vector.upper() + '_URL}}', escape(url, quote=True))
        page = page.replace('{{' + vector.upper() + '_CHANGE}}', escape(value))
        page = page.replace('{{' + vector.upper() + '_INDEXES}}', escape(description))
    return page.replace('{{RENT_START}}', EXAMPLE_START).replace('{{RENT_LATEST}}', latest)
