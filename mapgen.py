from PIL import Image
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

def genFixedRatioMap(in_map, out_map, value, ratio, **relate):
    assert in_map.size == out_map.size
    values = list(in_map.data)
    values.sort()
    threshold = values[int(ratio * in_map.size**2)]
    
    for i in range(in_map.size**2):
        if in_map.data[i] < threshold:
            if ('require' in relate) and not (out_map.data[i] in relate['require']):
                continue
            if ('avoid' in relate) and (out_map.data[i] in relate['avoid']):
                continue
            out_map.data[i] = value

MAPSIZE = 256 #obvious
LAND_AMOUNT = 0.5 #^^
LAND_WIBBLE_BASE = 60 #Large-scale wibbliness
LAND_WIBBLE_SCALE = 1.5 #Small-scale wibbliness (smaller is more wibbly).

TREE_AMOUNT = 0.2
TREE_WIBBLE_BASE = 10
TREE_WIBBLE_SCALE = 0.8

heightmap = genTerrainMap(MAPSIZE, LAND_WIBBLE_BASE, LAND_WIBBLE_SCALE)
terrainmap = SquareMap(MAPSIZE)
genFixedRatioMap(heightmap, terrainmap, TerrainType.GRASS, LAND_AMOUNT)
treemap = genTerrainMap(MAPSIZE, TREE_WIBBLE_BASE, TREE_WIBBLE_SCALE)
genFixedRatioMap(treemap, terrainmap, TerrainType.TREES, TREE_AMOUNT, avoid=[TerrainType.WATER])


img = Image.new( 'RGB', (MAPSIZE,MAPSIZE), "black")
pixels = img.load()

for i in range(img.size[0]):
    for j in range(img.size[1]):
        if terrainmap.get(i,j) == TerrainType.WATER:
            pixels[i,j] = (0,0,255)
        elif terrainmap.get(i,j) == TerrainType.GRASS:
            pixels[i,j] = (0,255,0)
        elif terrainmap.get(i,j) == TerrainType.TREES:
            pixels[i,j] = (64,127,64)

img.save("out.png")
