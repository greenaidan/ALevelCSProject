import pygame, copy, math, random, os, items_main, text


def interact(check,blocks):
    for block in blocks:
        if (check[0]<block[0]+block[2])and(check[0]+check[2]>block[0])and (check[1]<block[1]+block[3])and(check[1]+check[3]>block[1]):
            return True
    return False

def myround(x, base=5):
    return base * round(x/base)

def gen_player(path):
    file = open(path, "w")
    lines = []
    lines.append("100,100\n")
    lines.append("0,0\n")
    lines.append("10\n")
    lines.append("0,0\n")
    lines.append("0\n")
    lines.append("0\n")
    file.writelines(lines)
    file.close()

class Player:
    def __init__(self, save):
        a = "saves/" +save+"/player_data.txt"
        if not os.path.exists(a):
            gen_player(a)
            
        file = open(a,"r")
        file = list(map(lambda s: s.strip(),file))

        self.save = save
        self.pos = [int(x) for x in file[0].split(",")]
        self.loc = [int(x) for x in file[1].split(",")]
        self.visited = []

        for x in file[3].split(":"):
            x = x.split(",")
            self.visited.append([int(x[0]), int(x[1])])

        self.num_bombs = int(file[4])
        self.life_points_amount = int(file[5])
        
        self.health = int(file[2])
        self.rot = "d"
        self.speed_walk = 4
        self.speed_run = 6
        self.speed_slow = 3
        self.speed_lock = False
        self.oldpos = copy.deepcopy(self.pos)
        self.oldtick = 0
        self.rect = self.pos+[64,64]
        self.blood = []
        self.blood_tick = 0
        
        self.attack_tick = 0
        self.block_attack = False
        self.blow = False
        
        #self.visited = []
        self.move_room = False
        self.placed_bomb = True
        self.red = False

        self.max_lp = 30

        self.coffin = None
        self.dead = False

        a = "saves/" +save+"/coffin.txt"
        if os.path.exists(a):
            file = open(a,"r")
            file = list(map(lambda s: s.strip(),file))
        else:
            file = open(a,"w")
            file.writelines(["None\n"])
            file.close()
            file = ["None"]
            
        if file[0] != "None":
            pos = [int(x) for x in file[0].split(",")]
            room_pos = [int(x) for x in file[1].split(",")]
            health = int(file[2])
            bomb_num = int(file[3])
            self.coffin = items_main.Coffin(copy.deepcopy(pos),copy.deepcopy(room_pos), health, bomb_num)
        
       

    def save_player(self):
        a = "saves/" +self.save+"/player_data.txt"
        file = open(a,"w")
        lines = []
        lines.append(str(round(self.pos[0]))+","+str(round(self.pos[1]))+"\n")
        lines.append(str(self.loc[0])+","+str(self.loc[1])+"\n")
        lines.append(str(self.health)+"\n")
        line = ""
        c = 1
        for loc in self.visited:
            line+=str(loc[0])+","+str(loc[1])
            if c < len(self.visited):
                line+=":"
            c+=1
        line+="\n"
        lines.append(line)
        line = str(self.num_bombs)+"\n"
        lines.append(line)
        line = str(self.life_points_amount)+"\n"
        lines.append(line)
        file.writelines(lines)
        file.close()
        a = "saves/" +self.save+"/coffin.txt"
        file = open(a,"w")
        lines = []
        if self.coffin == None:
            lines.append("None\n")
        else:
            lines.append(str(int(self.coffin.pos[0]))+","+str(int(self.coffin.pos[1]))+"\n")
            lines.append(str(self.coffin.room_pos[0])+","+str(self.coffin.room_pos[1])+"\n")
            lines.append(str(self.health)+"\n")
            lines.append(str(self.num_bombs)+"\n")
        file.writelines(lines)
        file.close()
        
    def interact(check,blocks):
        for block in blocks:
            if (check[0]<block[0]+block[2])and(check[0]+check[2]>block[0])and (check[1]<block[1]+block[3])and(check[1]+check[3]>block[1]):
                return True
        return False
            
    def move(self, room, screen):
        #print(self.life_points_amount)
        #self.life_points_amount += 1
        
        self.red = False
        self.loc = room.loc
        self.move_room = False
        if not room.loc in self.visited:
            self.visited.append(room.loc)

        if self.health <= 0: self.health = 0; self.dead = True
        if self.life_points_amount > self.max_lp: self.life_points_amount = self.max_lp
            
        blocks = room.blocks
        enemies = room.enemies       
        blocks = copy.deepcopy(blocks)
        walls = copy.deepcopy(blocks)
        for x in enemies:
            blocks.append(x.rect)
        old_pos = copy.deepcopy(self.pos)
        move = [0,0]
        keys_hold = pygame.key.get_pressed()

        space_press = keys_hold[pygame.K_SPACE]

        if self.attack_tick > 0:
            self.attack_tick -= 1
            self.block_attack = True

        if self.block_attack and space_press:
            space_press = False
        elif not space_press and self.attack_tick == 0:
            self.block_attack = False
        
        if space_press and not self.block_attack:
            self.attack_tick = 15

        self.blow = self.attack_tick == 15

        if (self.attack_tick == 0):
            if(keys_hold[pygame.K_LSHIFT] and not self.speed_lock):
                movement_speed = self.speed_run
            elif (not self.speed_lock):
                movement_speed = self.speed_walk
            if(keys_hold[pygame.K_UP]):
                move[1]-=movement_speed
                self.rot = "u"
            if(keys_hold[pygame.K_DOWN]):
                move[1]+=movement_speed
                self.rot = "d"
            if(keys_hold[pygame.K_LEFT]):
                move[0]-=movement_speed
                self.rot = "l"
            if(keys_hold[pygame.K_RIGHT]): 
                move[0]+=movement_speed
                self.rot = "r"
                
            if(keys_hold[pygame.K_b] and not self.placed_bomb and self.num_bombs > 0):
                temp_bomb = items_main.Bomb(self.pos)
                c = 0
                for item in room.items:
                    if item.pos == temp_bomb.pos:
                        c += 1
                if c == 0:
                    room.items.append(items_main.Bomb(self.pos))
                    self.placed_bomb = True
                    self.num_bombs -= 1
            elif (not keys_hold[pygame.K_b] and self.placed_bomb):
                self.placed_bomb = False
            if(keys_hold[pygame.K_n]) and self.life_points_amount >= self.max_lp:
                self.coffin = items_main.Coffin(copy.deepcopy(self.pos), copy.deepcopy(self.loc), copy.deepcopy(self.health),copy.deepcopy(self.num_bombs))
                self.life_points_amount = 0
                self.save_player()
            
        
        test_rect = copy.deepcopy(self.rect)
        if self.rot == "u":test_rect[1] -= 64; test_rect[0] += 10; test_rect[2] =40
        if self.rot == "d":test_rect[1] += 64; test_rect[0] += 16; test_rect[2] =40
        if self.rot == "l":test_rect[0] -= 64; test_rect[1] += 16; test_rect[3] =40
        if self.rot == "r":test_rect[0] += 64; test_rect[1] += 16; test_rect[3] =40
        #pygame.draw.rect(screen, [255]*3, test_rect)


                
        if move[0]!= 0 and move[1] != 0:
            move[0] /= (2)**0.5
            move[1] /= (2)**0.5
        y = False
        x = False
        speed_lock = False
        
        if self.attack_tick == 0:
            if not interact([self.pos[0]+move[0],self.pos[1]]+[60,60],blocks):
                self.pos[0]+=move[0]
            else:
                speed_lock = True
                movement_speed = self.speed_slow
            if not interact([self.pos[0],self.pos[1]+move[1]]+[60,60],blocks):
                self.pos[1]+=move[1]
            else:
                speed_lock = True
                movement_speed = self.speed_slow
            self.rect = self.pos + [64,64]
            
        if (self.blow):
            for enemy in enemies:
                if interact(test_rect, [enemy.rect]):
                    
                    enemy.health -= 1
                    enemy.fly_back_tick = 9
                    enemy.been_hit_tick = 120
                    enemy.player_stabbed = True
        if self.blood_tick > 10:
            self.red = True
            
    def draw(self, screen, tick):
        if self.coffin != None and self.coffin.room_pos == self.loc:
            self.coffin.draw(screen)
        
        if self.blood_tick > 0:
            self.blood_tick -= 1
            self.add_blood(round(self.blood_tick/30 * 15))

        for blood in self.blood:
            if blood.tick > 0:
                blood.draw(screen)
            else:
                self.blood.remove(blood)
        
        if self.oldpos != self.pos:
            self.oldpos = copy.deepcopy(self.pos)
            self.oldtick = tick
        else: tick = self.oldtick
        pixel_pos = copy.deepcopy(self.pos)
        pixel_pos = [myround(pixel_pos[0], 4), myround(pixel_pos[1], 4)]


        x = 64; y = 64
        draw_pos = copy.deepcopy([myround(self.pos[0],4),myround(self.pos[1],4)])
        
        name = "mob_sprites/shadow.png"
        image = pygame.image.load(name)
        image_big = pygame.transform.scale(image,(64,64))
        screen.blit(image_big,[draw_pos[0],draw_pos[1]+4])
        
        name = self.rot
        
        if self.attack_tick > 0:
            if self.rot == "d": y = 128
            if self.rot == "u": y = 128; draw_pos[1] -= 64
            if self.rot == "l": x = 128; draw_pos[0] -= 64
            if self.rot == "r": x = 128
            name += "a.png"
        else:
            name+=str((tick//15)%2)+".png"
            
        name = "mob_sprites/player/" + name
        image = pygame.image.load(name)
        if self.blood_tick > 10:
            image.fill([255, 0, 0], special_flags=pygame.BLEND_MULT)
        image_big = pygame.transform.scale(image,(x,y))
        screen.blit(image_big,draw_pos)
            
        
    def draw_stats(self, screen):
        health = self.health
        off = health/2 - math.trunc(health/2)
        num_full = int(health/2 - off)
        num_half = int(off * 2)
        num_empty = 5-num_full-num_half
        x = 68
        y = 16
        scale = 32
        m = 5
        for i in range(num_full):
            if m != 0:
                image = pygame.image.load("misc_sprites/full_heart.png")
                image_big = pygame.transform.scale(image,(scale, scale))
                screen.blit(image_big,[x,y])
                x += 48
                m -= 1
        if num_half == 1 and m != 0:
            image = pygame.image.load("misc_sprites/half_heart.png")
            image_big = pygame.transform.scale(image,(scale, scale))
            screen.blit(image_big,[x,y])
            x += 48
            m -= 1
        for i in range(num_empty):
            if m != 0:
                image = pygame.image.load("misc_sprites/empty_heart.png")
                image_big = pygame.transform.scale(image,(scale, scale))
                screen.blit(image_big,[x,y])
                x += 48
                m -= 1

        bomb_count = str(self.num_bombs)
        if len(bomb_count) < 2:
            bomb_count = "0"+bomb_count
        t = text.Text([650,5], bomb_count)
        t.draw(screen)

        pygame.draw.rect(screen, [0]*3, [460,16,144,24])

        lp = self.life_points_amount
        if lp > self.max_lp: lp = self.max_lp
        across = myround((lp/self.max_lp) * 136,4)

        if (lp != 0):
            if lp == self.max_lp: colour = [212,175,55]
            else: colour = [20,155,0]
            pygame.draw.rect(screen, colour, [464,20,across,16])
        


    

        image = pygame.image.load("misc_sprites/bomb_small.png")
        image_big = pygame.transform.scale(image,(32, 32))
        screen.blit(image_big,[612,12])
        
        

    def draw_map(self, screen):
        centre = [374,374]
        for loc in self.visited:
            rel = [loc[0]-self.loc[0], loc[1]-self.loc[1]]
            pygame.draw.rect(screen, [255]*3, [centre[0]+rel[0]*20,centre[1]-rel[1]*20,20,20])
            pygame.draw.rect(screen, [0]*3, [centre[0]+rel[0]*20+4,centre[1]-rel[1]*20+4,12,12])
            
        pygame.draw.rect(screen, [255,0,0], [centre[0],centre[1],20,20])
            
    def add_blood(self, amount=5):
        pixel_pos = [myround(self.pos[0],4),myround(self.pos[1],4)]
        self.blood.append(Blood(pixel_pos ,amount, 600))

    def add_health(self, amount=5):
        self.health+=amount
        if self.health > 10:
            self.health = 10

class Blood:
    def __init__(self, pos, amount, tick):
        temp = pygame.Surface((64,64),pygame.SRCALPHA)
        
        for x in range (16):
            for y in range (16):
                if random.randint(1,100) < amount and x > 4 and x < 14 and y > 4 and y < 14:
                    pygame.draw.rect(temp, [random.randint(100,200),0,0], [x*4, y*4, 4, 4])
        self.blood_surf = temp
        self.pos = pos
        self.tick = tick
        
    def draw(self, screen):
        screen.blit(self.blood_surf, self.pos)
        self.tick -= 1
        
