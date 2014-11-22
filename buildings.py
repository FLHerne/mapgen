import numpy
import random
from PIL import Image
from hackystuff import *

class BuildingPlan(object):
    def __init__(self, filename):
        planfile = Image.open(filename).convert('L')
        self.layout = ~numpy.array(planfile, dtype=numpy.bool_)
        self.center = [a/2 for a in self.layout.shape]

def genBuildings(height_map, terrain_map, number):
    assert height_map.shape == terrain_map.shape
    building_positions = list()

    def tryCreateBuilding(topleft, plan):
        bottomright = (topleft[0] + plan.layout.shape[0],
                       topleft[1] + plan.layout.shape[1])
        if max(bottomright) >= height_map.shape[0]:
            return False  #FIXME Restriction shouldn't exist.
        site_height = height_map[topleft[0]:bottomright[0], topleft[1]:bottomright[1]]
        if site_height.max() - site_height.min() > 50:
            return False
        site_terrain = terrain_map[topleft[0]:bottomright[0], topleft[1]:bottomright[1]]
        site_costs = numpy.choose(site_terrain, ABuildCosts).sum()
        max_cost = 5 * plan.layout.shape[0] * plan.layout.shape[1]
        if site_costs > max_cost:
            return False
        site_terrain[:] = numpy.choose(plan.layout, [TerrainType.ROOFD, TerrainType.WALLS])
        return True

    max_attempts = number * 20
    attempts = 0
    buildingone = BuildingPlan("buildingtemplates/buildingone.png")
    while attempts < max_attempts and len(building_positions) < number:
        t_x = random.randint(0, terrain_map.shape[0])
        t_y = random.randint(0, terrain_map.shape[0])
        if tryCreateBuilding((t_x, t_y), buildingone):
            building_positions.append((t_x+buildingone.center[0], t_y+buildingone.center[1]))
        attempts += 1
    return building_positions
