"""Full-history all-items CPI for dollar conversion; no extrapolated years."""
import csv, json, math, re
from datetime import datetime, timezone
from pathlib import Path
from source import ROOT, rows
REGIONS=('Canada','British Columbia','Nova Scotia','Alberta','Saskatchewan','Manitoba','Ontario','Quebec','New Brunswick','Prince Edward Island','Newfoundland and Labrador')
SOURCE='https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401'
def add_observation(series,row):
    region=row.get('GEO');date=row.get('REF_DATE','')
    if region not in series or row.get('Products and product groups')!='All-items':return
    if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',date):raise ValueError('Invalid monthly date')
    if row.get('UOM')!='2002=100' or row.get('SCALAR_FACTOR')!='units':raise ValueError('Unexpected all-items CPI unit')
    if not row.get('VALUE'):return
    value=float(row['VALUE'])
    if not math.isfinite(value) or value<=0:raise ValueError('Invalid all-items index')
    if date in series[region]:raise ValueError('Duplicate all-items index')
    series[region][date]={'index':value,'status':row.get('STATUS',''),'vector':row.get('VECTOR','')}
def build_history(series):
    annual={};latest={};coverage={}
    for region,months in series.items():
        if not months:continue
        years={}
        for date,observation in sorted(months.items()):years.setdefault(date[:4],{})[date[5:]]=observation
        complete={}
        for year,values in years.items():
            if set(values)=={f'{m:02}' for m in range(1,13)}:
                complete[year]={'index':sum(v['index'] for v in values.values())/12,'months':12,'flags':sorted({v['status'] for v in values.values() if v['status']})}
        if not complete:continue
        annual[region]=complete
        last=max(months);latest[region]={'date':last,**months[last]}
        coverage[region]={'first_month':min(months),'last_month':last,'first_complete_year':min(complete),'last_complete_year':max(complete),'complete_years':len(complete)}
    return {'schema':'coolcode.dollar-history.v1','source':SOURCE,'method':'Annual indexes are arithmetic means of twelve published monthly all-items CPI observations, not partial-year averages. Latest-month comparisons are separately labelled. Index base: 2002=100; not seasonally adjusted.','regions':list(annual),'annual':annual,'latest_month':latest,'coverage':coverage}
def validate_history(data):
    if set(data['regions'])!=set(REGIONS):raise ValueError('A geography lacks complete annual history')
    if data['coverage']['Canada']['first_month']!='1914-01' or len(data['annual']['Canada'])<100:raise ValueError('Canadian historical series is truncated')
    if any(len(data['annual'][g])<40 for g in REGIONS):raise ValueError('Provincial history is truncated')
def publish_history(data):
    validate_history(data)
    data['checked_at']=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
    path=ROOT/'web/data/dollars.json';temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n');temporary.replace(path)
    print(json.dumps({'history_regions':len(data['regions']),'canada_first':min(data['annual']['Canada']),'canada_last_complete':max(data['annual']['Canada']),'latest_month':data['latest_month']['Canada']['date']}))
def main():
    series={region:{} for region in REGIONS};stream=rows('18100004');head=next(stream)
    for row in stream:
        if len(row)==len(head):add_observation(series,dict(zip(head,row)))
    publish_history(build_history(series))
if __name__=='__main__':main()
