import pygame, enemies_main, items_main, copy, os, random, noise, time


class room:
    def __init__(self, save, loc):
        #print(loc)
        self.loc = copy.deepcopy(loc)
        a = "saves/"+save+"/"+str(loc[0])+"_"+str(loc[1])+".txt"

        if not os.path.exists(a):
            gen_room(copy.deepcopy(a), copy.deepcopy(loc), save)
            print("doesn't exist", a)
            
        file = open(a, "r").readlines()
        file = list(map(lambda s: s.strip(),file))
        tiles = []

        for line in file:
            if line == ":ENDROOM:": break
            tiles.append(line.split(","))

        tile_dict = {}
        for line in tiles:
            for tile in line:
                if tile != "non":
                    name = "tile_sprites/"+tile+".png"
                    image = pygame.image.load(name)
                    image_big = pygame.transform.scale(image,(16*4,16*4))
                    tile_dict[tile] = image_big

        tile_data = open("tile_sprites/tile_data.txt", "r").readlines()
        tile_data = list(map(lambda s: s.strip(),tile_data))
        blockable = []
        for line in tile_data:
            if line.split(":")[1] == "1":
                blockable.append(line.split(":")[0])
        blocks = []
        y = 0
        for line in tiles:
            x = 0
            for tile in line:
                if tile in blockable:
                    blocks.append([x*64,y*64,64,64])
                x += 1
            y += 1
            
        enemies = []
        for line in file[file.index(":ENDROOM:")+1:]:
            if line == ":ENDMOB:": break
            line = line.split(":")
            loc = line[1].split(",")
            loc = [int(loc[0]), int(loc[1])]
            if line[0] == "Begazun":
                enemies.append(enemies_main.Begazun(loc,float(line[2]), float(line[3])))
                #enemies.append(enemies_main.Begazun(loc,1.5,3))
            if line[0] == "Taghut":
                enemies.append(enemies_main.Taghut(loc,float(line[2]), float(line[3])))
                
            if line[0] == "Siyah":
                enemies.append(enemies_main.Siyah(loc,float(line[2]), float(line[3])))

        acts = []
        goto_loc = []
        goto_room = []
        for line in file[file.index(":ENDMOB:")+1:]:
            if line == ":ENDACT:":break
            line = line.split(":")
            for line2 in line:
                line[line.index(line2)] = [int(x) for x in line2.split(",")]
            acts.append(line[0])
            goto_room.append(line[1])
            goto_loc.append(line[2])

        items = []
        for line in file[file.index(":ENDACT:")+1:]:
            if line == ":ENDITEMS:": break
            line = line.split(":")
            line[1] = int(line[1])
            line[2] = [int(x) for x in line[2].split(",")]
            if line[0] == "health":
                items.append(items_main.Health_bottle(line[1],line[2]))
            if line[0] == "bomb_add":
                items.append(items_main.Bomb_add(line[1],line[2]))
            
            

        doors = [int(x) for x in file[file.index(":ENDITEMS:")+1].split(",")]


        self.blockable = blockable
        self.doors = doors
        self.items = items        
        self.acts = acts
        self.goto_room = goto_room
        self.goto_loc = goto_loc
        self.blocks = blocks
        self.tile_dict = tile_dict
        self.tiles = tiles
        self.save = save
        self.enemies = enemies

    def update_blocks(self):

        tile_data = open("tile_sprites/tile_data.txt", "r").readlines()
        tile_data = list(map(lambda s: s.strip(),tile_data))
        blockable = []
        for line in tile_data:
            if line.split(":")[1] == "1":
                blockable.append(line.split(":")[0])
        self.blocks = []
        y = 0
        for line in self.tiles:
            x = 0
            for tile in line:
                if tile in blockable:
                    self.blocks.append([x*64,y*64,64,64])
                x += 1
            y += 1
        

    def move(self, player, screen, tick):
        for enemy in self.enemies:
            enemy.move(self, player, self.enemies, tick)
            if enemy.health <= 0:
                if enemy.player_stabbed:
                    if enemy.type in ["begazun", "Taghut"]:
                        if (random.randint(1,100) <= 30):
                            self.items.append(items_main.Health_bottle(3,[int(x) for x in enemy.pos]))
                    elif enemy.type in ["Siyah"]:
                        self.items.append(items_main.Bomb_add(1,[int(x) for x in enemy.pos]))
                self.items.append(items_main.Poof(enemy.pos, 10))
                self.items.append(items_main.Life_point_add(enemy.pos, enemy.life_points_add))
                self.enemies.remove(enemy)
                

        c = 0
        for item in self.items:
            if item.type == "life_point_add":
                item.update(player)
            if not item.type in ["bomb", "poof"]:
                if interact(player.rect, [item.rect]):
                    if item.type == "health":
                        player.add_health(item.gain)
                    if item.type == "bomb_add":
                        player.num_bombs += item.gain
                    if item.type == "life_point_add":
                        player.life_points_amount += item.amount
                    self.items.remove(item)
            else:
                item.update(self, player)
                if item.blow_tick == 0:
                    self.items.remove(item)
                
        for act in self.acts:
            if interact(player.rect, [act]):
                self.save_room()
                player.pos = copy.deepcopy(self.goto_loc[self.acts.index(act)])
                player.blood = []
                self.transition_room(copy.deepcopy(self.goto_room[self.acts.index(act)]), screen)
                player.move_room = True
                self.__init__(self.save, copy.deepcopy(self.goto_room[self.acts.index(act)]))
            c += 1
        
    def draw(self, screen, tick, pos = [0,0]):
        for y in range(len(self.tiles)):
            for x in range (len(self.tiles[y])):
                if self.tiles[y][x] != "non":
                    screen.blit(self.tile_dict[self.tiles[y][x]],[x*64+pos[0],y*64+pos[1]])


    def transition_room(self, new_loc, screen):
        diff = [-self.loc[0]+new_loc[0],-self.loc[1]+new_loc[1]]
        temp = room(self.save,new_loc)
        move_loc = [0,0]
        screen.fill([0]*3)
        clock = pygame.time.Clock()
        
        while 1:
            move_loc[0]-=diff[0]*24
            move_loc[1]+=diff[1]*24
            #print(move_loc)
            self.draw(screen, 0, move_loc)
            #print(diff)
            temp.draw(screen, 0, [move_loc[0]+diff[0]*768,move_loc[1]-diff[1]*768])
            
            pygame.display.update()
            
            if abs(move_loc[0]) == 768 or abs(move_loc[1]) == 768:
                break
            clock.tick(60)
    def draw_items(self, screen):
        for item in self.items: item.draw(screen)

    def draw_enemies(self, screen, tick):
        for enemy in self.enemies:
            enemy.draw(screen, tick)
        for enemy in self.enemies:
            enemy.draw_stats(screen)

    def save_room(self):
        file = open("saves/"+self.save+"/"+str(self.loc[0])+"_"+str(self.loc[1])+".txt","w")
        lines = []
        for y in range(len(self.tiles)):
            line = ""
            c = 1
            for x in range (len(self.tiles[0])):
                line+=self.tiles[y][x]
                if (c < len(self.tiles[y])):
                    line += ","
                c += 1
            lines.append(line+"\n")
        lines.append(":ENDROOM:\n")
        for enemy in self.enemies:
            line = enemy.type+":"+str(int(enemy.pos[0]))+","+str(int(enemy.pos[1]))+":"+str(enemy.speed)+":"+str(enemy.health)
            lines.append(line+"\n")
        lines.append(":ENDMOB:\n")
        c = 0
        for act in self.acts:
            line = str(act[0])+","+str(act[1])+","+str(act[2])+","+str(act[3])+":"
            line += str(self.goto_room[c][0])+","+str(self.goto_room[c][1])+":"
            line += str(self.goto_loc[c][0])+","+str(self.goto_loc[c][1])
            lines.append(line+"\n")
            c+=1
        lines.append(":ENDACT:\n")

        for item in self.items:
            if item.type in ["bomb", "poof", "life_point_add"]: continue
            line = item.type+":"
            line+=str(item.gain)+":"
            line+=str(item.pos[0])+","+str(item.pos[1])+"\n"
            lines.append(line)
        lines.append(":ENDITEMS:\n")

        line = ""
        c = 1
        for door in self.doors:
            line += str(door)
            if c < len(self.doors):
                line += ","
            c += 1
        lines.append(line)
        
        #print(lines)
        file.writelines(lines)
        file.close()



def draw_block(pos, name, screen):
    name+=".png"
    image = pygame.image.load(name)
    image_big = pygame.transform.scale(image,(16*4,16*4))
    screen.blit(image_big,pos)

def interact(check,blocks):
    for block in blocks:
        if (check[0]<block[0]+block[2])and(check[0]+check[2]>block[0])and (check[1]<block[1]+block[3])and(check[1]+check[3]>block[1]):
            return True
    return False

def exists(loc, save):
    #print("--",loc)
    path = "saves/" + save + "/" + str(loc[0]) + "_" + str(loc[1]) + ".txt"
    #print("--",path)
    return(os.path.exists(path))

def connect_door(loc, check, save, banned=False):
    if exists(check, save):
        diff = (check[0] - loc[0], check[1] - loc[1])
        check_room = room(save, check)
        dic = {
            ( 0, 1): 2,
            ( 0,-1): 0,
            ( 1, 0): 3,
            (-1, 0): 1,
        }
        ret = dic[diff] in check_room.doors
        if banned:
            return (not ret)
        else:
            return (ret)
    else:
        return (False)
    
# Compatibility shim
def banned_door(loc, check, save):
    return connect_door(loc, check, save, True)

def gen_room(path, loc, save):
    dist = ((loc[0])**2+(loc[1])**2)**0.5
    print((loc[0]**2 + loc[1]**2)**0.5)
    blank = open("blank_room.txt", "r")
    blank = list(map(lambda s: s.strip(),blank))
    lines = []
    
    tiles = []
    for line in blank:
        tiles.append(line.split(","))

    doors = []
    banned_doors = []

    if (connect_door(loc, [loc[0]+1,loc[1]], save)):
        doors.append(1)
    elif (banned_door(loc, [loc[0]+1,loc[1]], save)):
        banned_doors.append(1)
        
    if (connect_door(loc, [loc[0]-1,loc[1]], save)):
        doors.append(3)
    elif (banned_door(loc, [loc[0]-1,loc[1]], save)):
        banned_doors.append(3)

    if (connect_door(loc, [loc[0],loc[1]+1], save)):
        doors.append(0)
    elif (banned_door(loc, [loc[0],loc[1]+1], save)):
        banned_doors.append(0)

    if (connect_door(loc, [loc[0],loc[1]-1], save)):
        doors.append(2)
    elif (banned_door(loc, [loc[0],loc[1]-1], save)):
        banned_doors.append(2)

    print(doors, banned_doors)

    c = random.randint(1,100)
    if c < 10: c = 1
    elif c < 40: c = 2
    else: c = 3

    while len(doors) + len(banned_doors) < c:
        for c in range(4):
            if random.randint(1,10) < 4:
                if not c in doors+banned_doors:
                    doors.append(c)



    #doors = [0,1,2,3]

    if not 0 in doors:
        tiles[0][5] = "tp"
        tiles[0][6] = "tp"
        tiles[1][5] = "ts"
        tiles[1][6] = "ts"
    if not 1 in doors:
        tiles[5][11] = "er"
        tiles[6][11] = "er"
    if not 2 in doors:
        tiles[11][5] = "bp"
        tiles[11][6] = "bp"
    if not 3 in doors:
        tiles[5][0] = "el"
        tiles[6][0] = "el"
        tiles[5][1] = "ls"
        tiles[6][1] = "ls"
        
    y = 0
    enemies = []
    for line in tiles:
        x = 0
        temp_line = ""
        for tile in line:
            t = random.randint(0,8)
            if tile == "tp" and t < 3:
                tile = "tp"+str(t)
            if random.randint(1,50) < 2 and not x in [0,1,2,11] and not y in [0,1,11]:
                tile = "mc"+str(random.randint(0,1))
            scale = 12
            n = 0.5+noise.pnoise3(x/scale,y/scale,random.randint(1,10000),octaves=2,persistence=1,lacunarity=1,repeatx=64,repeaty=64, base = 2)
            if n > 0.7 and not y in [0,1,10,11] and not x in [0,1,10,11]:
                tile = "tt"
            elif (random.randint(1,100) < 6) and not y in [0,1,10,11] and not x in [0,1,10,11]:
                if random.randint(1,100) < 100/((dist**0.9) + 1):
                    enemies.append(enemies_main.Begazun([x*64, y*64], 1.5, 3))
                else:
                    if random.randint(1,100) < 80:
                        enemies.append(enemies_main.Taghut([x*64, y*64], 2, 5))
                    else:
                        enemies.append(enemies_main.Siyah([x*64, y*64], 3.5, 1))
            temp_line += tile
            if x+1 < len(line): temp_line +=","
            x+=1
        lines.append(temp_line+"\n")
        y+=1
    lines.append(":ENDROOM:\n")

    for enemy in enemies:
        line = enemy.type+":"+str(int(enemy.pos[0]))+","+str(int(enemy.pos[1]))+":"+str(enemy.speed)+":"+str(enemy.health)
        lines.append(line+"\n")
        
    lines.append(":ENDMOB:\n")

    if 0 in doors:
        line = "320,-10,128,10:"
        line += str(loc[0])+","+str(loc[1]+1)+":352,704\n"
        lines.append(line)

    if 2 in doors:
        line = "320,768,128,10:"
        line += str(loc[0])+","+str(loc[1]-1)+":352,0\n"
        lines.append(line)

    if 3 in doors:
        line = "-10,320,10,128:"
        line += str(loc[0]-1)+","+str(loc[1])+":704,350\n"
        lines.append(line)

    if 1 in doors:
        line = "768,320,10,128:"
        line += str(loc[0]+1)+","+str(loc[1])+":0,350\n"
        lines.append(line)
    lines.append(":ENDACT:\n")

    lines.append(":ENDITEMS:\n")
    
    line = ""
    c = 1
    for i in doors:
        line+=str(i)
        if c < len(doors):
            line+=","
        c += 1
        
    line += "\n"
    lines.append(line)

    file = open(path, "w")
    file.writelines(lines)
    file.close()


        
        

            
