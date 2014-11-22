import numpy

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
    ROOFD = 12
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
    TerrainType.ROOFD: 1,
    TerrainType.WALLS: 20,
    TerrainType.GLASS: 20
}

ABuildCosts = [BuildCosts[i] if i in BuildCosts else 0 for i in range(max(BuildCosts.keys())+1)]

TypeColors = {
    TerrainType.DEEPW: (0  , 0 ,255),
    TerrainType.WATER: (0  ,127,255),
    TerrainType.ROCKS: (127,127,127),
    TerrainType.BOGGY: (64 ,127,127),
    TerrainType.GRASS: (0  ,255,  0),
    TerrainType.SANDY: (127,127,  0),
    TerrainType.SNOWY: (255,255,255),
    TerrainType.TREES: (64 ,127, 64),
    TerrainType.PLANK: (127, 64,  0),
    TerrainType.FLOOR: (255,255,127),
    TerrainType.ROOFD: (128, 0 ,128),
    TerrainType.WALLS: (0  , 0 ,  0),
    TerrainType.GLASS: (0  ,255,255)
}

colordtype = numpy.dtype([('r', numpy.uint8), ('g', numpy.uint8), ('b', numpy.uint8)])
ATypeColors = numpy.array([TypeColors[i] if i in TypeColors else 0 for i in range(max(TypeColors.keys())+1)], dtype=colordtype)
