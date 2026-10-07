"""Four related estate tables: blocks -> vines -> harvests -> tastings."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import ripeness, score_label, vine_age, yield_band, yield_per_acre

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
