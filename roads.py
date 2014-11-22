import random
from constants import *
from hackystuff import *

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
