# Offline verification

From the repository root, using Python 3.10+ and Node 22+:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r examples/01-image-to-3d-character/python/requirements.txt
python -m unittest discover -s tests -p 'test_*.py'

cd examples/01-image-to-3d-character/typescript
npm install
npm run check
npx tsx --test ../../../tests/run.test.ts
```

The lifecycle tests replace the API client with fake responses and temporary files.
They cover interrupted/ambiguous submissions, resume, changed inputs, downloads, and
credit accounting without network access or API credentials. The cross-language test
runs every recipe in dry-run mode and compares its payloads and output names; install
the TypeScript dependencies above before running it:

```sh
# From the repository root, with the Python environment active:
python tests/check_recipes.py
```
