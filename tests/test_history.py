import unittest, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from history import add_observation,build_history
class HistoryTests(unittest.TestCase):
 def row(self,date,value='100',**extra):
  return {'GEO':'Canada','REF_DATE':date,'Products and product groups':'All-items','VALUE':value,'UOM':'2002=100','SCALAR_FACTOR':'units','STATUS':'','VECTOR':'v1',**extra}
 def test_complete_year_required_and_latest_month_separate(self):
  s={'Canada':{}}
  for m in range(1,13):add_observation(s,self.row(f'1914-{m:02}',str(m)))
  for m in range(1,11):add_observation(s,self.row(f'2026-{m:02}','200'))
  data=build_history(s)
  self.assertEqual(data['annual']['Canada']['1914']['index'],6.5)
  self.assertNotIn('2026',data['annual']['Canada'])
  self.assertEqual(data['latest_month']['Canada']['date'],'2026-10')
 def test_gap_or_suppression_never_fills_an_annual_average(self):
  s={'Canada':{}}
  for m in range(1,13):add_observation(s,self.row(f'2025-{m:02}','' if m==6 else '100'))
  self.assertEqual(build_history(s)['regions'],[])
 def test_duplicate_wrong_unit_and_nonfinite_fail(self):
  s={'Canada':{}};add_observation(s,self.row('1914-01'))
  with self.assertRaises(ValueError):add_observation(s,self.row('1914-01'))
  with self.assertRaises(ValueError):add_observation(s,self.row('1914-02',UOM='different'))
  with self.assertRaises(ValueError):add_observation(s,self.row('1914-02','nan'))
