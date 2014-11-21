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

ABuildCosts = [BuildCosts[i] if i in BuildCosts else 0 for i in range(max(BuildCosts.keys()))]
