"""Vineyard Estate API built with Pixeltable.

    pxt schema update app.py estate
    pxt service run app.py estate
"""
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

from udfs import ripeness, score_label, vine_age, yield_band, yield_per_acre

# ---- tables ----
TableModel = pxt.model_base()


class Blocks(TableModel, name='blocks'):
    block_id = pxt.Column(type=pxt.String, primary_key=True)
    name: pxt.String
    varietal: pxt.String
    acres: pxt.Float
    organic: pxt.Bool
    region: pxt.String
    irrigation: pxt.String | None        # added later; nullable, so the update is in place


class Vines(TableModel, name='vines'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    block_id: pxt.String
    clone: pxt.String
    rootstock: pxt.String
    planted_year: pxt.Int

    age = vine_age(planted_year)


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


class Tastings(TableModel, name='tastings'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    block_id: pxt.String
    vintage: pxt.Int
    score: pxt.Int
    notes: pxt.String | None

    label = score_label(score)


# ---- queries ----
@pxt.query
def open_blocks(min_acres: float):
    """Organic blocks of at least `min_acres`, largest first."""
    return Blocks.where((Blocks.acres >= min_acres) & (Blocks.organic == True)).select(  # noqa: E712
        Blocks.block_id, Blocks.name, Blocks.varietal, Blocks.acres, Blocks.irrigation
    ).order_by(Blocks.acres, asc=False)


@pxt.query
def block_harvests(block_id: str):
    """Harvest history for one block, oldest first."""
    return Harvests.where(Harvests.block_id == block_id).select(
        Harvests.picked_on, Harvests.tons, Harvests.tpa, Harvests.band, Harvests.brix, Harvests.ripe
    ).order_by(Harvests.picked_on)


# ---- routes ----
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
estate_api.add_query_route(path='/blocks/harvests', query=block_harvests, method='get')
