import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from rent import collect, validate


class RentalHistoryTests(unittest.TestCase):
    def test_names_units_and_vectors_identify_different_measures(self):
        series = {'v41692860': {}}
        row = {'VECTOR': 'v41692860', 'GEO': 'Halifax, Nova Scotia', 'Products and product groups': 'Rented accommodation',
               'COORDINATE': '8.80', 'UOM': '2002=100', 'SCALAR_FACTOR': 'units', 'REF_DATE': '2015-01', 'VALUE': '115.3'}
        collect(series, row)
        self.assertEqual(series['v41692860']['2015-01'], 115.3)
        with self.assertRaises(ValueError):
            collect(series, row)
        with self.assertRaises(ValueError):
            collect(series, {**row, 'Products and product groups': 'Rent'})
        collect(series, {**row, 'REF_DATE': '2015-02', 'VALUE': ''})
        self.assertNotIn('2015-02', series['v41692860'])

    def test_both_series_must_reach_release_month(self):
        with self.assertRaises(ValueError):
            validate({'v41692860': {'1971-01': 36, '2015-01': 115.3},
                      'v41691548': {'1978-09': 47.1, '2015-01': 113.7}}, '2026-10')
