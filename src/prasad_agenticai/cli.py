import json
import csv
from typing import List, Dict, Optional
import typer
from rich.console import Console
from rich.table import Table

from .scimago_map import load_scimago_csv
from .openalex import get_venue_id_by_issn, get_works_for_venue

app = typer.Typer()
console = Console()


@app.command()
def fetch_articles(
    quartile: str = typer.Option(..., help="Quartile value, e.g. Q1, Q2, Q3, Q4"),
    scimago_file: str = typer.Option(..., help="Path to Scimago CSV mapping (issn,quartile,venue_title)"),
    query: Optional[str] = typer.Option(None, help="Optional search query to narrow works"),
    limit: int = typer.Option(100, help="Maximum number of articles to fetch in total"),
    out: Optional[str] = typer.Option(None, help="Output file path (json or csv). If omitted, prints to stdout"),
    fmt: str = typer.Option('json', help="Output format: json or csv")
):
    """Fetch articles from OpenAlex for venues listed in the Scimago CSV under the given quartile."""
    quartile = quartile.upper()
    quartile_map = load_scimago_csv(scimago_file)
    issns = sorted(quartile_map.get(quartile, []))
    if not issns:
        console.print(f"[red]No ISSNs found for quartile {quartile} in {scimago_file}[/red]")
        raise typer.Exit(code=1)

    collected = []
    per_venue_limit = max(1, limit // max(1, len(issns)))
    for issn in issns:
        console.print(f"[cyan]Looking up venue for ISSN {issn}[/cyan]")
        venue_id = get_venue_id_by_issn(issn)
        if not venue_id:
            console.print(f"[yellow]No OpenAlex venue found for ISSN {issn} — skipping[/yellow]")
            continue
        console.print(f"[green]Found venue {venue_id}, fetching up to {per_venue_limit} works[/green]")
        works = get_works_for_venue(venue_id, query=query, limit=per_venue_limit)
        for w in works:
            item = {
                'title': w.get('title'),
                'doi': w.get('doi'),
                'authors': ';'.join([a.get('author', {}).get('display_name', '') for a in w.get('authorships', [])]),
                'abstract': w.get('abstract_inverted_index') and _reconstruct_abstract(w.get('abstract_inverted_index')) or w.get('abstract'),
                'concepts': ';'.join([c.get('display_name') for c in w.get('concepts', [])]) if w.get('concepts') else '',
                'publication_date': w.get('publication_date'),
                'venue_title': w.get('host_venue', {}).get('display_name'),
                'venue_issn': issn,
                'openalex_id': w.get('id'),
                'source_url': w.get('id')
            }
            collected.append(item)
            if len(collected) >= limit:
                break
        if len(collected) >= limit:
            break

    if out:
        fmt = fmt.lower()
        if fmt == 'json':
            with open(out, 'w', encoding='utf-8') as f:
                json.dump(collected, f, ensure_ascii=False, indent=2)
            console.print(f"[green]Wrote {len(collected)} records to {out}[/green]")
        elif fmt == 'csv':
            keys = ['title','doi','authors','abstract','concepts','publication_date','venue_title','venue_issn','openalex_id','source_url']
            with open(out, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for row in collected:
                    writer.writerow(row)
            console.print(f"[green]Wrote {len(collected)} records to {out}[/green]")
        else:
            console.print(f"[red]Unknown format {fmt} — use json or csv[/red]")
            raise typer.Exit(code=2)
    else:
        # print a small table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title", overflow='fold')
        table.add_column("DOI")
        table.add_column("Date")
        for r in collected[:50]:
            table.add_row(r.get('title') or '', r.get('doi') or '', r.get('publication_date') or '')
        console.print(table)


def _reconstruct_abstract(inv_index: dict) -> str:
    # OpenAlex sometimes returns abstract as inverted index; reconstruct if present
    # inverted index: word -> positions
    try:
        positions = []
        for word, locs in inv_index.items():
            for pos in locs:
                positions.append((pos, word))
        positions.sort()
        return ' '.join([w for _, w in positions])
    except Exception:
        return ''


if __name__ == '__main__':
    app()
