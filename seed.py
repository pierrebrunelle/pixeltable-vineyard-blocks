"""Seed three blocks, their vines, two harvests and a tasting.

Usage:
    python seed.py            # seeds the local `estate` catalog directory
    python seed.py my_dir     # or another directory you passed to `pxt schema update`
"""
import sys
from pathlib import Path

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'estate'
HERE = Path(__file__).resolve().parent

SEED = {
    'blocks': [
        {'block_id': 'N-12', 'name': 'North Bench', 'varietal': 'Cabernet Sauvignon', 'acres': 8.5, 'organic': True, 'region': 'Napa', 'irrigation': None},
        {'block_id': 'S-03', 'name': 'Creekside', 'varietal': 'Chardonnay', 'acres': 4.2, 'organic': False, 'region': 'Napa', 'irrigation': 'drip'},
        {'block_id': 'H-07', 'name': 'Hilltop', 'varietal': 'Syrah', 'acres': 6.0, 'organic': True, 'region': 'Napa', 'irrigation': 'dry-farmed'},
    ],
    'vines': [
        {'block_id': 'N-12', 'clone': '337', 'rootstock': '101-14', 'planted_year': 2004},
        {'block_id': 'H-07', 'clone': '877', 'rootstock': '110R', 'planted_year': 2015},
    ],
    'harvests': [
        {'block_id': 'N-12', 'picked_on': '2025-09-30', 'tons': 28.5, 'acres': 8.5, 'brix': 25.1},
        {'block_id': 'S-03', 'picked_on': '2025-09-02', 'tons': 21.0, 'acres': 4.2, 'brix': 22.4},
    ],
    'tastings': [
        {'block_id': 'N-12', 'vintage': 2023, 'score': 93, 'notes': 'Cassis, graphite, firm tannins'},
    ],
}

for table_name, rows in SEED.items():
    t = pxt.get_table(f'{target}/{table_name}')
    if t.count() > 0:
        print(f'{target}/{table_name} already has {t.count()} rows; skipping')
        continue
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str) and v.startswith('data/'):
                row[k] = str(HERE / v)   # local sample media file
    t.insert(rows)
    print(f'inserted {len(rows)} rows into {target}/{table_name}')
