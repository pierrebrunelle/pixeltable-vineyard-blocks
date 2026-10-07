"""Vineyard Estate API built with Pixeltable.

    pxt schema update app.py estate
    pxt service run app.py estate
"""
from pixeltable.serving import FastAPIRouter

from models import Blocks, Harvests, TableModel, Tastings, Vines  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import block_harvests, open_blocks

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
