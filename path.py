from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import copy

def create(enemy, player, room):
    tile_blocks = [] # y x 
    for line in room.tiles:
        line_add = []
        for tile in line:
            if tile in room.blockable:
                line_add.append(0)
            else:
                line_add.append(1)
        tile_blocks.append(line_add)

    for e in room.enemies:
        if e != enemy:
            tile_blocks[int((e.pos[0]+16)//64)][int((e.pos[1]+16)//64)] = 0

    start = copy.deepcopy([(enemy.pos[0]+16)//64, (enemy.pos[1]+16)//64]) # y x
    end = copy.deepcopy([(player.pos[0]+32)//64, (player.pos[1]+32)//64]) # y x
    

    grid = Grid(matrix=tile_blocks)
    start = grid.node(int(start[0]), int(start[1]))
    end = grid.node(int(end[0]), int(end[1]))

    finder = AStarFinder(diagonal_movement=DiagonalMovement.only_when_no_obstacle )
    path, runs = finder.find_path(start, end, grid)

    #print('operations:', runs, 'path length:', len(path))
    #print(grid.grid_str(path=path, start=start, end=end))
    p = []
    c = 0
    for loc in path:
        if c != 0:
            p.append([loc[0]*64+16, loc[1]*64+16])
        c+=1
    return(p)

    
