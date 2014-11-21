from PIL import Image
from constants import *
import diamondsquare
from hackystuff import *
import terraintypes
import random
import numpy

def genTerrainMap(size, base_wibble, wibble_scale):
    values = diamondsquare.genvaluemap(size, wibble_scale)
    values -= values.min()
    values *= 255.0/values.max()
    return values

def testRelIndex(index, out_map, **relate):
    if ('require' in relate) and not (out_map.flat[index] in relate['require']):
        return False
    if ('avoid' in relate) and (out_map.flat[index] in relate['avoid']):
        return False
    if 'req_omap' in relate and not all(n[0].flat[index] in n[1] for n in relate['req_omap']):
        return False
    if 'avd_omap' in relate and any(n[0].flat[index] in n[1] for n in relate['avd_omap']):
        return False
    return True

def genFixedRatioMap(in_map, out_map, value, ratio, **conditions):
    threshold = numpy.percentile(in_map, ratio*100)
    terraintypes.conditionMap((in_map < threshold), out_map, value, **conditions)
    return int(threshold)

def genBuildings(height_map, terrain_map, number):
    assert height_map.shape[0] == terrain_map.shape[0]
    buildings_created = list()

    def tryCreateBuilding(x, y, plan):
        max_cost = plan.w_x * plan.w_y * 5000
        max_height_diff = 1000
        buildcost = 0
        h_min = 255
        h_max= 0
        for ix in range(x, x+plan.w_x):
            for iy in range(y, y+plan.w_y):
                if ix >= height_map.shape[0] or iy >= height_map.shape[1]:
                    return False
                h_min = min(h_min, height_map[ix, iy])
                h_max = max(h_max, height_map[ix, iy])
                if h_max > h_min+max_height_diff:
                    return False
                buildcost += BuildCosts[terrain_map[ix, iy]]
                if buildcost > max_cost:
                    return False
        for ix in range(plan.w_x):
            for iy in range(plan.w_y):
                terrain_map[x+ix, y+iy] = TerrainType.WALLS if plan.layout[ix][iy] else TerrainType.ROOFD
        return True

    while len(buildings_created) < number:
        t_x = random.randint(0, terrain_map.shape[0])
        t_y = random.randint(0, terrain_map.shape[0])
        if tryCreateBuilding(t_x, t_y, buildingone):
            buildings_created.append((t_x+buildingone.centre[0], t_y+buildingone.centre[1]))
    return buildings_created

def genRoads(terrain_map, positions):
    def genRoad(startpos, endpos):
        '''Find the best direction to move towards the player'''
        PF_MAP_SIZE = MAP_SIZE/2
        def mindist(a, b, size):
            '''Distance between two values accounting for world wrapping'''
            return min((b-a)%size,(a-b)%size)

        def mapcoord(pfcoord):
            '''Get map coordinate from pathfinder one'''
            return ((startpos[0] + pfcoord[0] - PF_MAP_SIZE) % MAP_SIZE,
                    (startpos[1] + pfcoord[1] - PF_MAP_SIZE) % MAP_SIZE)

        foundtarget = False
        dijkstramap = [[[0, (PF_MAP_SIZE, PF_MAP_SIZE), False] for x in xrange(2*PF_MAP_SIZE)] for x in xrange(2*PF_MAP_SIZE)]
        import heapq
        openlist = []
        heapq.heappush(openlist, (0, (PF_MAP_SIZE, PF_MAP_SIZE)))
        curpos = None
        while openlist:
            curnode = heapq.heappop(openlist)
            curpos = curnode[1]
            if mapcoord(curpos) == tuple(endpos):
                foundtarget = True
                break
            if dijkstramap[curpos[0]][curpos[1]][2] == True:
                continue
            dijkstramap[curpos[0]][curpos[1]][2] = True
            curdist = dijkstramap[curpos[0]][curpos[1]][0]
            for nbrpos in [(curpos[0]-1, curpos[1]), (curpos[0], curpos[1]-1), (curpos[0]+1, curpos[1]), (curpos[0], curpos[1]+1)]:
                nbrpos = (nbrpos[0]%MAP_SIZE, nbrpos[1]%MAP_SIZE)
                terrain = terrain_map[mapcoord(nbrpos)[0], mapcoord(nbrpos)[1]]
                cost = BuildCosts[terrain]
                newdist = curdist+cost
                if dijkstramap[nbrpos[0]][nbrpos[1]][0] <= newdist and dijkstramap[nbrpos[0]][nbrpos[1]][0] != 0:
                    continue
                heurdist = newdist + 3*(mindist(endpos[0], mapcoord(nbrpos)[0], MAP_SIZE) +
                                        mindist(endpos[1], mapcoord(nbrpos)[1], MAP_SIZE))
                dijkstramap[nbrpos[0]][nbrpos[1]] = [newdist, curpos, False]
                heapq.heappush(openlist, (heurdist, nbrpos))
        if not foundtarget:
            print "Failed"
            return False
        while dijkstramap[curpos[0]][curpos[1]][1] != (PF_MAP_SIZE, PF_MAP_SIZE):
            curpos = dijkstramap[curpos[0]][curpos[1]][1]
            terrain = int(terrain_map[mapcoord(curpos)[0]][mapcoord(curpos)[1]])
            newterrain = TerrainType.PLANK if (terrain == TerrainType.WATER or terrain == TerrainType.DEEPW or terrain == TerrainType.BOGGY or terrain == TerrainType.SANDY) else TerrainType.ROOFD if (terrain == TerrainType.ROOFD or terrain == TerrainType.WALLS) else TerrainType.FLOOR
            terrain_map[mapcoord(curpos)[0], mapcoord(curpos)[1]] = newterrain

    roads_created = set()
    for pos in positions:
        for i in range(ROADS_PER_BUILDING):
            altpos = positions[random.randint(0, len(positions)-1)]
            if (pos, altpos) in roads_created or (altpos, pos) in roads_created:
                continue
            roads_created.add((pos, altpos))
            genRoad(pos, altpos)

# Heightmap for world
height_map = genTerrainMap(MAP_SIZE, LAND_WIBBLE_BASE, LAND_WIBBLE_SCALE)

# Blank map of terrain for world - initially all deep water
terrain_map = numpy.zeros((MAP_SIZE, MAP_SIZE))

# Generate normal-depth water
genFixedRatioMap(height_map, terrain_map, TerrainType.WATER, LAND_PROPORTION+(1-LAND_PROPORTION)*(1-DEEP_WATER_PROPORTION))

# Generate grass
waterline = genFixedRatioMap(height_map, terrain_map, TerrainType.GRASS, LAND_PROPORTION)

# Generate snow
snow_scatter_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, SNOW_WIBBLE_SCALE)
genFixedRatioMap(snow_scatter_map, terrain_map, TerrainType.SNOWY, SNOW_PROPORTION, req_omap=[(height_map,range(waterline+SNOW_MIN_HEIGHT,256))])

# Generate rocks (on grass, snow and shallow water)
rock_scatter_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, ROCK_WIBBLE_SCALE)
genFixedRatioMap(rock_scatter_map, terrain_map, TerrainType.ROCKS, ROCK_PROPORTION_GRASS, require=[TerrainType.GRASS])
genFixedRatioMap(rock_scatter_map, terrain_map, TerrainType.ROCKS, ROCK_PROPORTION_SNOW, require=[TerrainType.SNOWY])
genFixedRatioMap(rock_scatter_map, terrain_map, TerrainType.ROCKS, ROCK_PROPORTION_WATER, require=[TerrainType.WATER])

# Generate sandy beaches
sand_scatter_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, SAND_WIBBLE_SCALE)
genFixedRatioMap(sand_scatter_map, terrain_map, TerrainType.SANDY, SAND_PROPORTION, avoid=[TerrainType.ROCKS], req_omap=[(height_map,range(waterline-SAND_MAX_DEPTH, waterline+SAND_MAX_HEIGHT))])

# Generate bogs
bog_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, BOG_WIBBLE_SCALE)
genFixedRatioMap(bog_map, terrain_map, TerrainType.BOGGY, BOG_PROPORTION, avoid=[TerrainType.ROCKS], req_omap=[(height_map,range(waterline-BOG_MAX_DEPTH, waterline+BOG_MAX_HEIGHT))])

# Generate trees (on grass and snow)
tree_scatter_map = genTerrainMap(MAP_SIZE, SCATTER_WIBBLE_BASE, TREE_WIBBLE_SCALE)
genFixedRatioMap(tree_scatter_map, terrain_map, TerrainType.TREES, TREE_PROPORTION_GRASS, require=[TerrainType.GRASS])
genFixedRatioMap(tree_scatter_map, terrain_map, TerrainType.TREES, TREE_PROPORTION_SNOW, require=[TerrainType.SNOWY])

# Generate buildings
buildings = genBuildings(height_map, terrain_map, NUM_BUILDINGS)
genRoads(terrain_map, buildings)

terrain_img = Image.new('RGB',(MAP_SIZE,MAP_SIZE),"black")
t_pixels = terrain_img.load()
heightmap_img = Image.new('L',(MAP_SIZE,MAP_SIZE),"black")
h_pixels = heightmap_img.load()

for i in range(MAP_SIZE):
    for j in range(MAP_SIZE):
        h_pixels[i,j] = height_map[i,j]
        terrain = terrain_map[i,j]
        t_pixels[i,j] = (
            (0  , 0 ,255) if terrain == TerrainType.DEEPW else
            (0  ,127,255) if terrain == TerrainType.WATER else
            (127,127,127) if terrain == TerrainType.ROCKS else
            (64 ,127,127) if terrain == TerrainType.BOGGY else
            (0  ,255,  0) if terrain == TerrainType.GRASS else
            (127,127,  0) if terrain == TerrainType.SANDY else
            (255,255,255) if terrain == TerrainType.SNOWY else
            (64 ,127, 64) if terrain == TerrainType.TREES else
            (127, 64,  0) if terrain == TerrainType.PLANK else
            (255,255,127) if terrain == TerrainType.FLOOR else
            (128, 0 ,128) if terrain == TerrainType.ROOFD else
            (0  , 0 ,  0) if terrain == TerrainType.WALLS else
            (0  ,255,255) if terrain == TerrainType.GLASS else
            None) # This shouln't happen!
terrain_img.save("terrain.png")
heightmap_img.save("heightmap.png")
