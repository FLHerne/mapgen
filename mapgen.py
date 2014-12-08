from PIL import Image
import buildings
from constants import *
import diamondsquare
from hackystuff import *
import rivers
import roads
import terraintypes
import random
import numpy

def genTerrainMap(size, base_wibble, wibble_scale):
    values = diamondsquare.genvaluemap(size, wibble_scale)
    values -= values.min()
    values *= 255.0/values.max()
    return values

def genFixedRatioMap(in_map, out_map, value, ratio, **conditions):
    threshold = numpy.percentile(in_map, ratio*100)
    terraintypes.conditionMap((in_map < threshold), out_map, value, **conditions)
    return int(threshold)

# Heightmap for world
height_map = genTerrainMap(MAP_SIZE, LAND_WIBBLE_BASE, LAND_WIBBLE_SCALE)

# Blank map of terrain for world - initially all deep water
terrain_map = numpy.zeros((MAP_SIZE, MAP_SIZE), dtype=numpy.uint8)

# Generate normal-depth water
genFixedRatioMap(height_map, terrain_map, TerrainType.WATER, LAND_PROPORTION+(1-LAND_PROPORTION)*(1-DEEP_WATER_PROPORTION))

# Generate grass
waterline = genFixedRatioMap(height_map, terrain_map, TerrainType.GRASS, LAND_PROPORTION)

# Generate snow
#snow_scatter_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, SNOW_WIBBLE_SCALE)
#genFixedRatioMap(snow_scatter_map, terrain_map, TerrainType.SNOWY, SNOW_PROPORTION, req_omap=[(height_map,range(waterline+SNOW_MIN_HEIGHT,256))])

# Generate rocks (on grass, snow and shallow water)
#rock_scatter_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, ROCK_WIBBLE_SCALE)
#genFixedRatioMap(rock_scatter_map, terrain_map, TerrainType.ROCKS, ROCK_PROPORTION_GRASS, require=[TerrainType.GRASS])
#genFixedRatioMap(rock_scatter_map, terrain_map, TerrainType.ROCKS, ROCK_PROPORTION_SNOW, require=[TerrainType.SNOWY])
#genFixedRatioMap(rock_scatter_map, terrain_map, TerrainType.ROCKS, ROCK_PROPORTION_WATER, require=[TerrainType.WATER])

# Generate sandy beaches
#sand_scatter_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, SAND_WIBBLE_SCALE)
#genFixedRatioMap(sand_scatter_map, terrain_map, TerrainType.SANDY, SAND_PROPORTION, avoid=[TerrainType.ROCKS], req_omap=[(height_map,range(waterline-SAND_MAX_DEPTH, waterline+SAND_MAX_HEIGHT))])

# Generate bogs
#bog_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, BOG_WIBBLE_SCALE)
#genFixedRatioMap(bog_map, terrain_map, TerrainType.BOGGY, BOG_PROPORTION, avoid=[TerrainType.ROCKS], req_omap=[(height_map,range(waterline-BOG_MAX_DEPTH, waterline+BOG_MAX_HEIGHT))])

# Generate trees (on grass and snow)
#tree_scatter_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, TREE_WIBBLE_SCALE)
#genFixedRatioMap(tree_scatter_map, terrain_map, TerrainType.TREES, TREE_PROPORTION_GRASS, require=[TerrainType.GRASS])
#genFixedRatioMap(tree_scatter_map, terrain_map, TerrainType.TREES, TREE_PROPORTION_SNOW, require=[TerrainType.SNOWY])

# Generate buildings
#buildings = buildings.genBuildings(height_map, terrain_map, NUM_BUILDINGS)
#roads.genRoads(terrain_map, buildings)
rivers.genRivers(height_map, terrain_map, 40)

heightmap_img = Image.fromarray(height_map.astype(numpy.uint8))
terrain_colors = numpy.choose(terrain_map, ATypeColors)
terrain_colors_3d = terrain_colors.view(dtype=numpy.uint8).reshape(MAP_SIZE,MAP_SIZE,3)
terrain_img = Image.fromarray(terrain_colors_3d)

terrain_img.save("terrain.png")
heightmap_img.save("heightmap.png")
