from PIL import Image
from constants import *
import random

class TerrainType:
    WATER = 0
    GRASS = 1
    TREES = 2
    PLANK = 3
    BRICK = 4
    GLASS = 5

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

def genTerrainMap(size, base_wibble, wibble_scale):
    values = SquareMap(size)
    values.put(0,0,128)
    
    def fillSquare(x, y, scale, alt):
        mean_val = (values.get(x-scale, y-scale) + values.get(x+scale, y-scale) + values.get(x-scale, y+scale) + values.get(x+scale, y+scale)) / 4
        rand_val = mean_val + random.randint(-alt, alt)
        values.put(x, y, rand_val)
    
    def fillDiamond(x, y, scale, alt):
        mean_val = (values.get(x-scale, y) + values.get(x, y-scale) + values.get(x+scale, y) + values.get(x, y+scale)) / 4
        rand_val = mean_val + random.randint(-alt, alt)
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
    
    scale = size / 2
    alt = base_wibble
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

def genFixedRatioMap(in_map, out_map, value, ratio, **relate):
    assert in_map.size == out_map.size
    values = list(in_map.data)
    values.sort()
    threshold = values[int(ratio * in_map.size**2)]
    
    for i in range(in_map.size**2):
        if in_map.data[i] < threshold:
            if testRelIndex(i, out_map, **relate):
                out_map.data[i] = value

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
            valid_nbrs = filter(lambda n: n[0] >= terrain_map.get(t_x, t_y) and terrain_map.get(*n[1]) != TerrainType.WATER, nbr_heights)
            if len(valid_nbrs) == 0:
                break
            t_x = valid_nbrs[0][1][0]
            t_y = valid_nbrs[0][1][1]
            terrain_map.put(t_x, t_y, TerrainType.WATER)
        streams_created += 1


height_map = genTerrainMap(MAP_SIZE, LAND_WIBBLE_BASE, LAND_WIBBLE_SCALE)
terrain_map = SquareMap(MAP_SIZE)
genFixedRatioMap(height_map, terrain_map, TerrainType.GRASS, LAND_AMOUNT)
treemap = genTerrainMap(MAP_SIZE, TREE_WIBBLE_BASE, TREE_WIBBLE_SCALE)
genFixedRatioMap(treemap, terrain_map, TerrainType.TREES, TREE_AMOUNT, avoid=[TerrainType.WATER])
genStreams(height_map, terrain_map, NUM_STREAMS)

img = Image.new('RGB',(MAP_SIZE,MAP_SIZE),"black")
pixels = img.load()

for i in range(MAP_SIZE):
    for j in range(MAP_SIZE):
        if terrain_map.get(i,j) == TerrainType.WATER:
            pixels[i,j] = (0,0,255)
        elif terrain_map.get(i,j) == TerrainType.PLANK:
            pixels[i,j] = (255,0,0)
        elif terrain_map.get(i,j) == TerrainType.GRASS:
            pixels[i,j] = (0,255,0)
        elif terrain_map.get(i,j) == TerrainType.TREES:
            pixels[i,j] = (64,127,64)


img.save("out.png")
