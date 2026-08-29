# prasadagenticai

This branch adds a small Python CLI "agent" that uses a Scimago CSV mapping (ISSN → quartile)
and OpenAlex to fetch article metadata (title, DOI, authors, abstract, concepts) for journals in
a selected Scimago quartile.

Files added:
- requirements.txt
- src/prasad_agenticai/ (package)
  - cli.py (Typer CLI)
  - openalex.py (OpenAlex helpers)
  - scimago_map.py (CSV loader)
- scripts/run_agent.sh (example)
- scimago_mapping_example.csv (small example mapping)

Usage example (after installing requirements):

python -m prasad_agenticai.cli fetch-articles --quartile Q1 --scimago-file scimago_mapping_example.csv --query "neuroscience" --limit 50 --out results.json --fmt json

Notes:
- Provide an authoritative Scimago CSV mapping for accurate quartiles. The example CSV is only illustrative.
- OpenAlex is used for works/abstracts and does not require an API key. Set a polite email in the User-Agent string in openalex.py.
