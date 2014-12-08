import random
import numpy
from hackystuff import TerrainType, neighbours, ATypeColors
from constants import MAP_SIZE
from PIL import Image

def genRivers(height_map, terrain_map, number):
    created = 0
    while created < number:
        t_x = random.randint(0, terrain_map.shape[0]-1)
        t_y = random.randint(0, terrain_map.shape[1]-1)
        cur_pos = (t_x, t_y)
        if terrain_map[cur_pos] in [TerrainType.WATER, TerrainType.DEEPW]:
            continue
        while True:
            terrain_map[cur_pos] = TerrainType.DEEPW
            nbrs = [(coord, height_map[coord], terrain_map[coord]) for coord in neighbours(cur_pos)]
            nbrs = filter(lambda x: x[2] not in [TerrainType.WATER, TerrainType.DEEPW], nbrs)
            if not nbrs:
                created += 1
                print 'broke!', created
                break
            lowest_nbr = sorted(nbrs, key=lambda x: x[1], reverse=True)[0]
            if lowest_nbr[1] < height_map[cur_pos]:
                height_map[lowest_nbr[0]] = height_map[cur_pos]
            cur_pos = lowest_nbr[0]
