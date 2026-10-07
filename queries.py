"""Estate queries."""
import pixeltable as pxt

from models import Blocks, Harvests


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
