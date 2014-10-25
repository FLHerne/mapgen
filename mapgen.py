from PIL import Image
from constants import *
import random

class TerrainType:
    DEEPW = 0
    WATER = 9
    ROCKS = 10
    BOGGY = 11
    GRASS = 1
    SANDY = 2
    SNOWY = 3
    TREES = 4
    PLANK = 5
    FLOOR = 6
    WALLS = 7
    GLASS = 8

BuildCosts = {
    TerrainType.DEEPW: 80,
    TerrainType.WATER: 40,
    TerrainType.ROCKS: 8,
    TerrainType.BOGGY: 24,
    TerrainType.GRASS: 4,
    TerrainType.SANDY: 6,
    TerrainType.SNOWY: 10,
    TerrainType.TREES: 8,
    TerrainType.PLANK: 1,
    TerrainType.FLOOR: 1,
    TerrainType.WALLS: 20,
    TerrainType.GLASS: 20
}

class BuildingPlan:
    def __init__(self, *layout):
        self.layout = zip(*layout)
        self.w_x = len(layout[0])
        self.w_y = len(self.layout[0])
        self.centre = (int(self.w_x/2), int(self.w_y/2))

buildingone = BuildingPlan(
[1,1,1,1,0,1,1],
[1,0,0,0,0,0,1],
[0,0,0,0,0,0,1],
[1,0,0,0,0,0,1],
[1,1,1,1,1,1,1])

class SquareMap:
    def __init__(self, size):
        self.size = size
        self.data = bytearray(size**2)
    def get(self, x, y):
        return self.data[(y % self.size) * self.size + (x % self.size)]
    def put(self, x, y, val):
        val = 0 if val < 0 else val
        val = 255 if val > 255 else val
        self.data[(y % self.size) * self.size + (x % self.size)] = val

def genTerrainMap(size, base_wibble, wibble_scale, force_edge=False, edge_range=None):
    if not ((size & (size - 1)) == 0) and size != 0:
        print("MAP_SIZE must be a power of two!")
        exit(1)
    values = SquareMap(size)

    def fillSquare(x, y, scale, alt):
        mean_val = (values.get(x-scale, y-scale) + values.get(x+scale, y-scale) + values.get(x-scale, y+scale) + values.get(x+scale, y+scale)) / 4
        rand_val = mean_val + random.randint(-alt, alt)
        if force_edge and (x == 0 or y == 0 or x == MAP_SIZE-1 or y ==MAP_SIZE-1):
            values.put(x, y, sorted(edge_range+(rand_val,))[1])
        else:
            values.put(x, y, rand_val)

    def fillDiamond(x, y, scale, alt):
        mean_val = (values.get(x-scale, y) + values.get(x, y-scale) + values.get(x+scale, y) + values.get(x, y+scale)) / 4
        rand_val = mean_val + random.randint(-alt, alt)
        if force_edge and (x == 0 or y == 0 or x == MAP_SIZE-1 or y ==MAP_SIZE-1):
            values.put(x, y, sorted(edge_range+(rand_val,))[1])
        else:
            values.put(x, y, rand_val)

    def fillAllSquare(scale, alt):
        c_y = scale
        while c_y < size:
            c_x = scale
            while c_x < size:
                fillSquare(c_x, c_y, scale, alt)
                c_x += scale * 2
            c_y += scale * 2

    def fillAllDiamond(scale, alt):
        c_y = 0
        while c_y < size:
            c_x = scale
            while c_x < size:
                fillDiamond(c_x, c_y, scale, alt)
                c_x += scale * 2
            c_y += scale
            c_x = 0
            while c_x < size:
                fillDiamond(c_x, c_y, scale, alt)
                c_x += scale * 2
            c_y += scale

    alt = base_wibble
    if force_edge:
        values.put(0, 0, sum(edge_range)/2)
        values.put(size/2, size/2, 128)
        fillAllDiamond(size/2, alt)
        scale = size/4
    else:
        values.put(0, 0, 128)
        scale = size / 2
    while (scale >= 1):
        fillAllSquare(scale, alt)
        fillAllDiamond(scale, alt)
        scale /= 2
        alt = int(alt/wibble_scale)

    return values

def testRelIndex(index, out_map, **relate):
    if ('require' in relate) and not (out_map.data[index] in relate['require']):
        return False
    if ('avoid' in relate) and (out_map.data[index] in relate['avoid']):
        return False
    if 'req_omap' in relate and not all(n[0].data[index] in n[1] for n in relate['req_omap']):
        return False
    if 'avd_omap' in relate and any(n[0].data[index] in n[1] for n in relate['avd_omap']):
        return False
    return True

def genFixedRatioMap(in_map, out_map, value, ratio, force_threshold=False, threshold_range=None, **relate):
    assert in_map.size == out_map.size
    if ratio <= 0 or ratio >= 1:
        print("*_PROPORTION constants must be between 0 and 1!")
        exit(1)
    values = list(in_map.data)
    values.sort()
    threshold = values[MAP_SIZE**2 - int(ratio * in_map.size**2)]
    if force_threshold:
        new_threshold = sorted(threshold_range + (threshold,))[1]
        if new_threshold != threshold:
            #print "Threshold forced from", threshold, "to", new_threshold
            threshold = new_threshold
    for i in range(in_map.size**2):
        if in_map.data[i] >= threshold:
            if testRelIndex(i, out_map, **relate):
                out_map.data[i] = value
    return  threshold

def genStreams(height_map, terrain_map, number):
    assert height_map.size == terrain_map.size

    def neighbours(in_map, x, y):
        def pvt(i,j):
            return (in_map.get(i,j),(i,j))
        return [pvt(x-1,y), pvt(x,y-1), pvt(x+1,y), pvt(x,y+1)]

    streams_created = 0
    while streams_created < number:
        t_x = random.randint(0, terrain_map.size)
        t_y = random.randint(0, terrain_map.size)
        if terrain_map.get(t_x, t_y) != TerrainType.WATER:
            continue
        nbr_terrain = neighbours(terrain_map, t_x, t_y)
        if [item[0] for item in nbr_terrain].count(TerrainType.WATER) == 4:
            continue
        while True:
            nbr_heights = neighbours(height_map, t_x, t_y)
            nbr_heights.sort()
            valid_nbrs = filter(lambda n: n[0] >= height_map.get(t_x, t_y) and terrain_map.get(*n[1]) != TerrainType.WATER, nbr_heights)
            if len(valid_nbrs) == 0:
                break
            t_x = valid_nbrs[0][1][0]
            t_y = valid_nbrs[0][1][1]
            terrain_map.put(t_x, t_y, TerrainType.WATER)
        streams_created += 1

def genBuildings(height_map, terrain_map, number):
    assert height_map.size == terrain_map.size
    buildings_created = list()

    def tryCreateBuilding(x, y, plan):
        max_cost = plan.w_x * plan.w_y * 5
        max_height_diff = 1000
        buildcost = 0
        h_min = 255
        h_max= 0
        for ix in range(x, x+plan.w_x):
            for iy in range(y, y+plan.w_y):
                h_min = min(h_min, height_map.get(ix, iy))
                h_max = max(h_max, height_map.get(ix, iy))
                if h_max > h_min+max_height_diff:
                    return False
                buildcost += BuildCosts[terrain_map.get(ix, iy)]
                if buildcost > max_cost:
                    return False
        for ix in range(plan.w_x):
            for iy in range(plan.w_y):
                terrain_map.put(x+ix, y+iy, TerrainType.WALLS if plan.layout[ix][iy] else TerrainType.FLOOR)
        return True

    while len(buildings_created) < number:
        t_x = random.randint(0, terrain_map.size)
        t_y = random.randint(0, terrain_map.size)
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

        dijkstramap = [[[0, (PF_MAP_SIZE, PF_MAP_SIZE), False] for x in xrange(2*PF_MAP_SIZE)] for x in xrange(2*PF_MAP_SIZE)]
        import heapq
        openlist = []
        heapq.heappush(openlist, (0, (PF_MAP_SIZE, PF_MAP_SIZE)))
        curpos = None
        while openlist:
            curnode = heapq.heappop(openlist)
            curdist = curnode[0]
            curpos = curnode[1]
            if mapcoord(curpos) == tuple(endpos):
                break
            if dijkstramap[curpos[0]][curpos[1]][2] == True:
                continue
            else:
                dijkstramap[curpos[0]][curpos[1]][2] = True
            for nbrpos in [(curpos[0]-1, curpos[1]), (curpos[0], curpos[1]-1), (curpos[0]+1, curpos[1]), (curpos[0], curpos[1]+1)]:
                if (nbrpos[0] < 0 or nbrpos[1] < 0 or
                    nbrpos[0] >= 2*PF_MAP_SIZE or nbrpos[1] >= 2*PF_MAP_SIZE or
                    nbrpos == (PF_MAP_SIZE, PF_MAP_SIZE)):
                    continue
                terrain = terrain_map.get(*mapcoord(nbrpos))
                cost = BuildCosts[terrain]
                newdist = curdist+cost
                if dijkstramap[nbrpos[0]][nbrpos[1]][0] <= newdist and dijkstramap[nbrpos[0]][nbrpos[1]][0] != 0:
                    continue
                dijkstramap[nbrpos[0]][nbrpos[1]] = [newdist, curpos, False]
                heapq.heappush(openlist, (newdist, nbrpos))
        while dijkstramap[curpos[0]][curpos[1]][1] != (PF_MAP_SIZE, PF_MAP_SIZE):
            curpos = dijkstramap[curpos[0]][curpos[1]][1]
            terrain = terrain_map.get(*mapcoord(curpos))
            newterrain = TerrainType.PLANK if (terrain == TerrainType.WATER or terrain == TerrainType.DEEPW or terrain_map == TerrainType.BOGGY or terrain == TerrainType.SANDY) else TerrainType.FLOOR
            terrain_map.put(mapcoord(curpos)[0], mapcoord(curpos)[1], newterrain)

    roads_created = set()
    for pos in positions:
        for i in range(ROADS_PER_BUILDING):
            altpos = positions[random.randint(0, len(positions)-1)]
            if (pos, altpos) in roads_created or (altpos, pos) in roads_created:
                continue
            roads_created.add((pos, altpos))
            genRoad(pos, altpos)

# Heightmap for world
height_map = genTerrainMap(MAP_SIZE, LAND_WIBBLE_BASE, LAND_WIBBLE_SCALE, True, (EDGE_MIN,EDGE_MAX))

# Blank map of terrain for world - initially all deep water
terrain_map = SquareMap(MAP_SIZE)

# Generate normal-depth water
genFixedRatioMap(height_map, terrain_map, TerrainType.WATER, LAND_PROPORTION+(1-LAND_PROPORTION)*(1-DEEP_WATER_PROPORTION))

# Generate grass
waterline = genFixedRatioMap(height_map, terrain_map, TerrainType.GRASS, LAND_PROPORTION, FORCE_SEA_EDGES, (EDGE_MAX+2,256))

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

# Generate streams
genStreams(height_map, terrain_map, NUM_STREAMS)

# Generate buildings
buildings = genBuildings(height_map, terrain_map, NUM_BUILDINGS)
genRoads(terrain_map, buildings)

terrain_img = Image.new('RGB',(MAP_SIZE,MAP_SIZE),"black")
t_pixels = terrain_img.load()
heightmap_img = Image.new('L',(MAP_SIZE,MAP_SIZE),"black")
h_pixels = heightmap_img.load()

for i in range(MAP_SIZE):
    for j in range(MAP_SIZE):
        h_pixels[i,j] = height_map.get(i,j)
        if terrain_map.get(i,j) == TerrainType.DEEPW:
            t_pixels[i,j] = (0,0,255)
        elif terrain_map.get(i,j) == TerrainType.WATER:
            t_pixels[i,j] = (0,127,255)
        elif terrain_map.get(i,j) == TerrainType.ROCKS:
            t_pixels[i,j] = (127,127,127)
        elif terrain_map.get(i,j) == TerrainType.BOGGY:
            t_pixels[i,j] = (64,127,127)
        elif terrain_map.get(i,j) == TerrainType.GRASS:
            t_pixels[i,j] = (0,255,0)
        elif terrain_map.get(i,j) == TerrainType.SANDY:
            t_pixels[i,j] = (127,127,0)
        elif terrain_map.get(i,j) == TerrainType.SNOWY:
            t_pixels[i,j] = (255,255,255)
        elif terrain_map.get(i,j) == TerrainType.TREES:
            t_pixels[i,j] = (64,127,64)
        elif terrain_map.get(i,j) == TerrainType.PLANK:
            t_pixels[i,j] = (127,64,0)
        elif terrain_map.get(i,j) == TerrainType.FLOOR:
            t_pixels[i,j] = (255,255,127)
        elif terrain_map.get(i,j) == TerrainType.WALLS:
            t_pixels[i,j] = (0,0,0)
        elif terrain_map.get(i,j) == TerrainType.GLASS:
            t_pixels[i,j] = (0,255,255)
terrain_img.save("terrain.png")
heightmap_img.save("heightmap.png")
