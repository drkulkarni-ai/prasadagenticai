import time
import requests
from typing import List, Dict, Optional

OPENALEX_BASE = "https://api.openalex.org"


class OpenAlexError(Exception):
    pass


def _get(url: str, params: Dict = None, max_retries: int = 5) -> Dict:
    headers = {"User-Agent": "prasadagenticai (mailto:your-email@example.com)"}
    for attempt in range(1, max_retries + 1):
        resp = requests.get(url, params=params or {}, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code in (429, 503):
            # rate limited or service unavailable — backoff
            wait = attempt * 2
            time.sleep(wait)
            continue
        # other errors
        raise OpenAlexError(f"OpenAlex returned {resp.status_code}: {resp.text}")
    raise OpenAlexError("Failed after retries")


def get_venue_id_by_issn(issn: str) -> Optional[str]:
    """Return OpenAlex venue id for an ISSN, or None if not found."""
    url = f"{OPENALEX_BASE}/venues"
    params = {"filter": f"issn:{issn}"}
    data = _get(url, params)
    results = data.get('results', [])
    if not results:
        return None
    # return the first venue id
    return results[0].get('id')


def get_works_for_venue(venue_id: str, query: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """Fetch works for a venue id. Optionally filter by a query (searched in title/abstract).

    Returns up to `limit` works (may be fewer).
    """
    url = f"{OPENALEX_BASE}/works"
    page_size = 200 if limit > 200 else limit
    params = {"filter": f"host_venue.id:{venue_id}", "per-page": page_size}
    if query:
        params["search"] = query
    works = []
    cursor = None
    while len(works) < limit:
        if cursor:
            params['cursor'] = cursor
        data = _get(url, params)
        results = data.get('results', [])
        works.extend(results)
        meta = data.get('meta', {})
        next_cursor = meta.get('next_cursor') or meta.get('next')
        if not next_cursor or not results:
            break
        cursor = next_cursor
        # safety: avoid tight loop
        time.sleep(0.1)
    return works[:limit]
