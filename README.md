# prasadagenticai

Initial repository for the Scimago + OpenAlex agent to fetch articles from journals by Scimago quartile.

This repository will hold a small Python CLI that:

- Loads a Scimago CSV mapping file (ISSN -> quartile).
- Queries OpenAlex for works published in venues that match a selected quartile.
- Outputs article metadata including title, DOI, authors, abstract, and concepts (as keywords) to JSON or CSV.

See branch `feature/scimago-openalex-agent` for the implementation.
