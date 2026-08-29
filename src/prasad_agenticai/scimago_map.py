import csv
from collections import defaultdict
from typing import Dict, Set


def load_scimago_csv(path: str) -> Dict[str, Set[str]]:
    """Load a Scimago CSV mapping file with columns: issn,quartile,venue_title

    ISSNs may be separated by semicolons in the issn field. Returns a mapping
    quartile (e.g. 'Q1') -> set of ISSN strings (normalized).
    """
    quartile_map = defaultdict(set)
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            issn_cell = row.get('issn') or row.get('ISSN') or ''
            quartile = (row.get('quartile') or row.get('Quartile') or '').strip()
            if not quartile or not issn_cell:
                continue
            issns = [s.strip() for s in issn_cell.split(';') if s.strip()]
            for issn in issns:
                # basic normalization: keep as-is; callers should ensure correct formatting
                quartile_map[quartile.upper()].add(issn)
    return quartile_map
