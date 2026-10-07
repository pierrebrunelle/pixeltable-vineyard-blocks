<!-- pixeltable-example-app: 20261003-vineyard-blocks -->
# Vineyard Estate API built with Pixeltable

[![Built with Pixeltable](https://img.shields.io/badge/built%20with-Pixeltable-5b4bff)](https://pixeltable.com)
[![PyPI - pixeltable](https://img.shields.io/pypi/v/pixeltable?label=pixeltable)](https://pypi.org/project/pixeltable/)
[![GitHub stars](https://img.shields.io/github/stars/pixeltable/pixeltable?style=social)](https://github.com/pixeltable/pixeltable)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Model a wine estate as four related tables: **blocks** (the parcels, keyed by block id), the **vines** planted in them, each block's **harvests** and the resulting **tastings**. Vine age, yield in tons per acre, a yield band, ripeness from Brix and a tasting label are **computed columns** backed by plain Python UDFs. One `FastAPIRouter` exposes inserts for every table, a stateless `/yield-band` calculator and `@pxt.query` routes for open blocks and per-block harvest history.

[Pixeltable](https://pixeltable.com) is open-source, Python-native **multimodal AI data infrastructure**: tables, incremental computed columns, UDFs, indexes and serving in one library, running locally or on Pixeltable Cloud.

> ⭐ **Like this example?** Star [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable) on GitHub. It helps other developers find it.

## What this example shows

- **Multi-table layout and schema evolution** with `pxt schema update`
- **`pixeltable.toml` project config**: local and Pixeltable Cloud database sizing in one file
- **FastAPI serving**: one `FastAPIRouter` turns tables and `@pxt.query` functions into typed REST routes (insert, update, delete, compute and query) with OpenAPI docs
- **Incremental computed columns** powered by plain Python UDFs (`@pxt.udf`)
- **Importable UDF module**: UDFs in `udfs.py`, tables in `models.py`, queries in `queries.py`, routes in `app.py` (Pixeltable resolves UDFs by module path)
- **`pixeltable.toml`** declares a local database and a **Pixeltable Cloud** database, so the same code deploys with `pxt db update`

## Evolving a multi-table schema

The four tables live in `models.py` and are created together by `pxt schema update app.py estate`. The schema is meant to change:

- **Add a column**: `irrigation: pxt.String | None` on `Blocks` is nullable, so adding it to an existing catalog is an in-place, non-destructive `pxt schema update`. Existing rows get `None`, and you can backfill them with `Blocks.update(...)`.
- **Change a query**: `open_blocks` filters on acreage *and* `organic`. Edit the body of a `@pxt.query` and `pxt schema check` / `pxt service update` notice the change. The service restarts with the new query, and nothing in the tables has to move.
- **Add a computed column**: declare it in the model and rerun `pxt schema update`. Pixeltable computes it for the rows that already exist.

## Stateless calculators

`POST /yield-band` is a **compute route**. It runs the `yield_band` and `yield_per_acre` expressions on `{"tons": ..., "acres": ...}` without writing a row, and only the inputs it declares are required.

## What's inside

| File | What it is |
|------|------------|
| `app.py` | The API: one `FastAPIRouter` wiring the tables and queries into REST routes |
| `client_demo.py` | Plant, harvest and taste through the API, then query open blocks and harvest history |
| `models.py` | Tables declared as Python classes: columns, computed columns, indexes |
| `pixeltable.toml` | Project config: the local database plus a Pixeltable Cloud database (sizing, deploy excludes) |
| `queries.py` | `@pxt.query` functions served as query routes |
| `seed.py` | Seed three blocks, their vines, two harvests and a tasting |
| `udfs.py` | Pixeltable UDFs (`@pxt.udf`) in their own importable module |
| `requirements.txt` / `pyproject.toml` | Dependencies (`pixeltable[serve]>=0.7.14`) |

**Tables**

| Table | Stored columns | Computed columns |
|-------|---------|------------------|
| `blocks` | `block_id`, `name`, `varietal`, `acres`, `organic`, `region`, `irrigation` | - |
| `vines` | `block_id`, `clone`, `rootstock`, `planted_year` | `id`, `age` |
| `harvests` | `block_id`, `picked_on`, `tons`, `acres`, `brix` | `id`, `tpa`, `band`, `ripe` |
| `tastings` | `block_id`, `vintage`, `score`, `notes` | `id`, `label` |

**API routes** (service `estate_api`)

| Method | Path | Kind | Backed by | Notes |
|--------|------|------|-----------|-------|
| `POST` | `/blocks` | insert | `Blocks` |  |
| `POST` | `/vines` | insert | `Vines` |  |
| `POST` | `/harvests` | insert | `Harvests` |  |
| `POST` | `/tastings` | insert | `Tastings` |  |
| `POST` | `/blocks/irrigation` | update | `Blocks` |  |
| `POST` | `/yield-band` | compute | `Harvests` |  |
| `GET` | `/blocks/open` | query | `open_blocks` |  |
| `GET` | `/blocks/harvests` | query | `block_harvests` |  |

## Quickstart

Requires Python 3.11+ and `pixeltable[serve]>=0.7.14`.

```bash
git clone https://github.com/pierrebrunelle/pixeltable-vineyard-blocks.git
cd pixeltable-vineyard-blocks
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create the tables in a local catalog directory named `estate`
pxt schema update app.py estate

python seed.py estate
pxt service run app.py estate --port 8000   # open http://localhost:8000/docs
python client_demo.py                      # in another terminal
pxt ls estate --tree --counts              # the four tables and their row counts
```

Try it:

```bash
curl -s -X POST localhost:8000/yield-band -H 'Content-Type: application/json' -d '{"tons": 28.5, "acres": 8.5}'
curl -s 'localhost:8000/blocks/open?min_acres=5'
```

## Deploy to Pixeltable Cloud

The same `app.py` runs on [Pixeltable Cloud](https://pixeltable.com). Sign in (or get a free trial database with `pxt new`), point the second database entry in `pixeltable.toml` at your own database, then deploy:

```bash
pxt login                       # or: export PIXELTABLE_API_KEY=<your-api-key>
# edit pixeltable.toml: name = 'pxt://<your-org>:<your-db>'
pxt db update pxt://<your-org>:<your-db>                 # build the image and upload the project
pxt schema update app.py pxt://<your-org>:<your-db>/estate   # create the tables in the hosted database
pxt service update app.py pxt://<your-org>:<your-db>/estate  # start the API there
pxt service list pxt://<your-org>:<your-db>              # list hosted services
```

Hosted routes require an API key: send it in the `X-api-key` header (for example `-H "X-api-key: $PIXELTABLE_API_KEY"`). Keep keys in environment variables or `pxt secret set`, never in code.

## Code walkthrough

**1. Business logic is plain Python, in `udfs.py`.** A `@pxt.udf` function can be used as a column expression. Pixeltable records UDFs by module path (`udfs.vine_age`), so they live in their own importable module rather than inline in the app: the daemon, serving workers and Pixeltable Cloud import it again by that path.

```python
# udfs.py
@pxt.udf
def vine_age(planted_year: int) -> int:
    return max(0, SEASON - planted_year)
```

**2. Tables are Python classes (`models.py`).** Annotated attributes are stored columns; attributes assigned an expression are **computed columns** (`id`, `tpa`, `band`, `ripe`), evaluated incrementally on every insert or update and recomputed when their inputs change.

```python
# models.py
class Harvests(TableModel, name='harvests'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    block_id: pxt.String
    picked_on: pxt.String
    tons: pxt.Float
    acres: pxt.Float
    brix: pxt.Float

    tpa = yield_per_acre(tons, acres)
    band = yield_band(tons, acres)
    ripe = ripeness(brix)
```

**3. Queries are functions (`queries.py`).** `@pxt.query` wraps a Pixeltable query so it can be called from Python or exposed as a route:

```python
# queries.py
@pxt.query
def open_blocks(min_acres: float):
    """Organic blocks of at least `min_acres`, largest first."""
    return Blocks.where((Blocks.acres >= min_acres) & (Blocks.organic == True)).select(  # noqa: E712
        Blocks.block_id, Blocks.name, Blocks.varietal, Blocks.acres, Blocks.irrigation
    ).order_by(Blocks.acres, asc=False)
```

**4. One router, a full REST API.** `FastAPIRouter` generates request/response models from the column types, validates input, and publishes OpenAPI docs at `/docs`:

```python
# app.py
estate_api = FastAPIRouter(name='estate_api')
estate_api.add_insert_route(Blocks, path='/blocks',
                            inputs=[Blocks.block_id, Blocks.name, Blocks.varietal, Blocks.acres, Blocks.organic,
                                    Blocks.region, Blocks.irrigation],
                            outputs=[Blocks.block_id])
estate_api.add_insert_route(Vines, path='/vines',
                            inputs=[Vines.block_id, Vines.clone, Vines.rootstock, Vines.planted_year],
                            outputs=[Vines.id, Vines.age])
estate_api.add_insert_route(Harvests, path='/harvests',
                            inputs=[Harvests.block_id, Harvests.picked_on, Harvests.tons, Harvests.acres, Harvests.brix],
                            outputs=[Harvests.id, Harvests.tpa, Harvests.band, Harvests.ripe])
estate_api.add_insert_route(Tastings, path='/tastings',
                            inputs=[Tastings.block_id, Tastings.vintage, Tastings.score, Tastings.notes],
                            outputs=[Tastings.id, Tastings.label])
estate_api.add_update_route(Blocks, path='/blocks/irrigation', inputs=[Blocks.irrigation],
                            outputs=[Blocks.block_id, Blocks.irrigation])
estate_api.add_compute_route(Harvests, path='/yield-band', inputs=[Harvests.tons, Harvests.acres],
                             outputs=[Harvests.tpa, Harvests.band])
estate_api.add_query_route(path='/blocks/open', query=open_blocks, method='get')
# ... more routes in app.py
```

## Learn more

- 🌐 Website: https://pixeltable.com
- 📚 Docs: https://docs.pixeltable.com
- 💻 Source: https://github.com/pixeltable/pixeltable (⭐ star it if Pixeltable is useful to you)
- 📦 PyPI: https://pypi.org/project/pixeltable/

---

<sub>Built as part of a daily series of Pixeltable example apps · Pixeltable 0.7.14 · Python, FastAPI, incremental computed columns · Licensed under Apache-2.0.</sub>
