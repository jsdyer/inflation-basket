"""Extract eight major CPI components and corresponding published basket weights."""
from source import rows, publish

REGIONS = ('Canada','British Columbia','Nova Scotia','Alberta','Saskatchewan','Manitoba','Ontario','Quebec','New Brunswick','Prince Edward Island','Newfoundland and Labrador')
CATEGORIES = ('Food','Shelter','Household operations, furnishings and equipment','Clothing and footwear','Transportation','Health and personal care','Recreation, education and reading','Alcoholic beverages, tobacco products and recreational cannabis','All-items')
def read_table(code):
    stream=rows(code); head=next(stream)
    for row in stream:
        if len(row)==len(head): yield dict(zip(head,row))
def main():
    series={g:{} for g in REGIONS}
    count=0
    for r in read_table('18100004'):
        g=r['GEO']; cat=r['Products and product groups']; date=r['REF_DATE']
        if g not in series or cat not in CATEGORIES or date < '2002-01' or not r['VALUE']: continue
        if r['UOM']!='2002=100' or r['SCALAR_FACTOR']!='units':raise ValueError('Unexpected CPI base')
        vals=series[g].setdefault(date,[None]*len(CATEGORIES)); pos=CATEGORIES.index(cat)
        if vals[pos] is not None:raise ValueError('Duplicate component per region and month')
        vals[pos]=float(r['VALUE']);count+=1
    weights={g:{} for g in REGIONS}
    for r in read_table('18100007'):
        g=r['GEO']; cat=r['Products and product groups']
        if (g not in weights or cat not in CATEGORIES[:-1] or not r['VALUE']
            or r['Price period of weight']!='Weight at basket reference period prices'
            or r['Geographic distribution of weight']!='Distribution to selected geographies'):continue
        weights[g].setdefault(r['REF_DATE'],[None]*8)[CATEGORIES.index(cat)]=float(r['VALUE'])
    current={}
    for g in REGIONS:
        complete=[year for year,vals in weights[g].items() if None not in vals and abs(sum(vals)-100)<0.15]
        year=max(complete);current[g]={'year':year,'values':weights[g][year]}
        if len(series[g])<240:raise ValueError(f'Truncated region {g}')
    months=sorted(series['Canada'])
    if not all(series[g].get(months[-1]) and None not in series[g][months[-1]] for g in REGIONS):raise ValueError('Incomplete final month')
    publish({'regions':REGIONS,'categories':CATEGORIES,'months':months,'series':series,'weights':current},
            dict(start=months[0],end=months[-1],count=count))
if __name__=='__main__': main()
