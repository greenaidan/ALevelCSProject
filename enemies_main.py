import pygame, copy, path, items_main

def distvec(vec):
    return((vec[0]**2 + vec[1]**2)**0.5)

def myround(x, base=5):
    return base * round(x/base)

def interact(check,blocks):
    for block in blocks:
        if (check[0]<block[0]+block[2])and(check[0]+check[2]>block[0])and (check[1]<block[1]+block[3])and(check[1]+check[3]>block[1]):
            return True
    return False

class Walker:
    def __init__(self, pos, speed, health):
        self.pos = pos 
        self.speed = speed
        self.health = health
        self.rot = "d"
        self.rect = self.pos+[32,32]
        self.player_stabbed = False
        self.been_hit_tick = 0
        
    def interact(self,blocks, diff, true_x, player_rect):
        if true_x:
            for block in blocks:
                if block != self.rect:
                    if (self.pos[0]-diff[0]<block[0]+block[2])and(self.pos[0]+32-diff[0]>block[0])and (self.pos[1]<block[1]+block[3])and(self.pos[1]+32>block[1]):
                        if block == player_rect:
                            self.player_damage = True
                        return True
            return False
        else:
            for block in blocks:
                if block != self.rect:
                    if (self.pos[0]<block[0]+block[2])and(self.pos[0]+32>block[0])and (self.pos[1]-diff[1]<block[1]+block[3])and(self.pos[1]-diff[1]+32>block[1]):
                        if block == player_rect:
                            self.player_damage = True
                        return True
            return False
        
    def draw(self, screen, tick):
        pixel_pos = copy.deepcopy(self.pos)
        pixel_pos = [myround(pixel_pos[0], 4), myround(pixel_pos[1], 4)]
        name = "mob_sprites/"+self.type+"/"+self.rot+str((tick//15)%2)+".png"
        image = pygame.image.load(name)
        if self.red:
            image.fill([255, 0, 0], special_flags=pygame.BLEND_MULT)
        image_big = pygame.transform.scale(image,(32,32))
        screen.blit(image_big,(pixel_pos[0], pixel_pos[1]))
        
    def draw_stats(self, screen):
        if self.been_hit_tick > 0:
            pixel_pos = copy.deepcopy(self.pos)
            pixel_pos = [myround(pixel_pos[0], 4), myround(pixel_pos[1], 4)]
            pixel_pos[0] -= 4
            pixel_pos[1] -= 16
            pygame.draw.rect(screen,[0]*3, pixel_pos+[40,12])
            health_ratio = self.health/self.max_health
            across = health_ratio * 32
            across = int(myround(across, base=4))
            pixel_pos[0] += 4
            pixel_pos[1] += 4
            pygame.draw.rect(screen,[255,0,0], pixel_pos+[across,4])
        
class Siyah(Walker):
    def __init__(self, pos, speed, health):
        super().__init__(pos, speed, health)
        self.type = "Siyah"
        self.player_damage = False
        self.fly_back_tick = 0
        self.red = False
        self.pos_queue = []
        self.update_queue_tick = 1
        self.explode_tick = 40
        self.max_health = 1
        self.life_points_add = 1
        
        
    def move(self, room, player, other_enemies, tick):
        if self.been_hit_tick >0: self.been_hit_tick -= 1
        explode_rect = [self.pos[0]-32,self.pos[1]-32, 96,96]
        if not interact(explode_rect, [player.rect]):
            self.explode_tick = 40
            blocks = room.blocks
            self.update_queue_tick -= 1
            if self.update_queue_tick == 0 or len(self.pos_queue) == 0:
                pre_queue = copy.deepcopy(self.pos_queue)
                self.update_queue_tick = 5
                self.pos_queue = path.create(self, player, room)

            self.red = False

            blocks = copy.deepcopy(blocks)
            blocks += [[320,0,128,64],[320,704,128,64],[0,320,64,128],[704,320,64,128]]

            try:
                pos = self.pos_queue[0]
                if len(self.pos_queue[0]) == 1:
                    pos = copy.deepcopy(player.pos)
            except:
                pos = copy.deepcopy(player.pos)

            blocks = copy.deepcopy(blocks)
            for enemy in other_enemies:
                blocks.append(enemy.rect)
            blocks.append(player.rect)
                
            old_pos = copy.deepcopy(self.pos)
            diff_temp = [self.pos[0]-pos[0],self.pos[1]-pos[1]]
            mag = distvec([self.pos[0]-pos[0],self.pos[1]-pos[1]])
            if mag < 2:
                self.pos_queue.pop(0)
            diff = [0,0]

            if self.fly_back_tick > 0:
                self.red = True
                if abs(diff_temp[0]) > abs(diff_temp[1]):
                    diff[0] = 8 * -diff_temp[0]/abs(diff_temp[0])
                else:
                    diff[1] = 8 * -diff_temp[1]/abs(diff_temp[1])
            else:
                diff = [diff_temp[0]*self.speed/mag,diff_temp[1]*self.speed/mag]
                
            if mag > 3:
                if not self.interact(blocks, diff, True, player.rect):
                    self.pos[0] -= diff[0]
                if not self.interact(blocks, diff, False, player.rect):
                    self.pos[1] -= diff[1]
                
            if abs(diff_temp[1]) > abs(diff_temp[0]):
                if diff_temp[1] < 0: self.rot = "d"
                else: self.rot = "u"
            else:
                if diff_temp[0] < 0: self.rot = "r"
                else: self.rot = "l"
        else:
            self.explode_tick -= 1
            #print(self.explode_tick)
            if self.explode_tick == 0:
                self.health = 0
                b = items_main.Bomb(self.pos)
                b.blow_tick = 15
                b.bomb_off = True
                room.items.append(b)

        c = 0
        ct = 0
        for enemy in other_enemies:
            if ((enemy.pos[0]-self.pos[0])**2 + (enemy.pos[1]-self.pos[1])**2)**0.5 < 45:
                ct = enemy.fly_back_tick
            if ct > c:
                c = ct
        self.fly_back_tick = c
        if self.fly_back_tick > 0:
            self.fly_back_tick -= 1
        self.rect = self.pos + [32,32]

class Begazun(Walker):
    def __init__(self, pos, speed, health):
        super().__init__(pos, speed, health)
        self.type = "Begazun"
        self.player_damage = False
        self.fly_back_tick = 0
        self.red = False
        self.max_health = 3
        self.life_points_add = 2
        
    def move(self, room, player, other_enemies, tick):
        if self.been_hit_tick >0: self.been_hit_tick -= 1
        blocks = room.blocks
        self.red = False

        blocks = copy.deepcopy(blocks)
        blocks += [[320,0,128,64],[320,704,128,64],[0,320,64,128],[704,320,64,128]]
        
        pos = [player.pos[0]+16, player.pos[1]+16]
        blocks = copy.deepcopy(blocks)
        for enemy in other_enemies:
            blocks.append(enemy.rect)
        blocks.append(player.rect)
            
        old_pos = copy.deepcopy(self.pos)
        diff_temp = [self.pos[0]-pos[0],self.pos[1]-pos[1]]
        mag = distvec(diff_temp)
        diff = [0,0]

        if self.fly_back_tick > 0:
            self.red = True
            if abs(diff_temp[0]) > abs(diff_temp[1]):
                diff[0] = 8 * -diff_temp[0]/abs(diff_temp[0])
            else:
                diff[1] = 8 * -diff_temp[1]/abs(diff_temp[1])
        else:
            diff = [diff_temp[0]*self.speed/mag,diff_temp[1]*self.speed/mag]
            
        if mag > 3:
            if not self.interact(blocks, diff, True, player.rect):
                self.pos[0] -= diff[0]
            if not self.interact(blocks, diff, False, player.rect):
                self.pos[1] -= diff[1]
            
        if abs(diff_temp[1]) > abs(diff_temp[0]):
            if diff_temp[1] < 0: self.rot = "d"
            else: self.rot = "u"
        else:
            if diff_temp[0] < 0: self.rot = "r"
            else: self.rot = "l"

        if self.player_damage:
            if tick % 20 == 0:
                player.health -= 1
                if player.blood_tick < 20:
                    player.blood_tick = 20
                self.player_damage = False

        c = 0
        ct = 0
        for enemy in other_enemies:
            if ((enemy.pos[0]-self.pos[0])**2 + (enemy.pos[1]-self.pos[1])**2)**0.5 < 45:
                ct = enemy.fly_back_tick
            if ct > c:
                c = ct
        self.fly_back_tick = c
        if self.fly_back_tick > 0:
            self.fly_back_tick -= 1
        self.rect = self.pos + [32,32]

        
class Taghut(Walker):
    def __init__(self, pos, speed, health):
        super().__init__(pos, speed, health)
        self.player_damage = False
        self.fly_back_tick = 0
        self.red = False
        self.type = "Taghut"
        self.pos_queue = []
        self.update_queue_tick = 1
        self.max_health = 5
        self.life_points_add = 3
        
    def move(self, room, player, other_enemies, tick):
        if self.been_hit_tick >0: self.been_hit_tick -= 1
        blocks = room.blocks
        self.update_queue_tick -= 1
        if self.update_queue_tick == 0 or len(self.pos_queue) == 0:
            pre_queue = copy.deepcopy(self.pos_queue)
            self.update_queue_tick = 5
            self.pos_queue = path.create(self, player, room)

        self.red = False

        blocks = copy.deepcopy(blocks)
        blocks += [[320,0,128,64],[320,704,128,64],[0,320,64,128],[704,320,64,128]]

        try:
            pos = self.pos_queue[0]
            if len(self.pos_queue[0]) == 1:
                pos = copy.deepcopy(player.pos)
        except:
            pos = copy.deepcopy(player.pos)

        blocks = copy.deepcopy(blocks)
        for enemy in other_enemies:
            blocks.append(enemy.rect)
        blocks.append(player.rect)
            
        old_pos = copy.deepcopy(self.pos)
        diff_temp = [self.pos[0]-pos[0],self.pos[1]-pos[1]]
        mag = distvec([self.pos[0]-pos[0],self.pos[1]-pos[1]])
        if mag < 2:
            self.pos_queue.pop(0)
        diff = [0,0]

        if self.fly_back_tick > 0:
            self.red = True
            if abs(diff_temp[0]) > abs(diff_temp[1]):
                diff[0] = 8 * -diff_temp[0]/abs(diff_temp[0])
            else:
                diff[1] = 8 * -diff_temp[1]/abs(diff_temp[1])
        else:
            diff = [diff_temp[0]*self.speed/mag,diff_temp[1]*self.speed/mag]
            
        if mag > 3:
            if not self.interact(blocks, diff, True, player.rect):
                self.pos[0] -= diff[0]
            if not self.interact(blocks, diff, False, player.rect):
                self.pos[1] -= diff[1]
            
        if abs(diff_temp[1]) > abs(diff_temp[0]):
            if diff_temp[1] < 0: self.rot = "d"
            else: self.rot = "u"
        else:
            if diff_temp[0] < 0: self.rot = "r"
            else: self.rot = "l"

        if self.player_damage:
            if tick % 20 == 0:
                player.health -= 2
                if player.blood_tick < 20:
                    player.blood_tick = 20
                self.player_damage = False

        c = 0
        ct = 0
        for enemy in other_enemies:
            if ((enemy.pos[0]-self.pos[0])**2 + (enemy.pos[1]-self.pos[1])**2)**0.5 < 45:
                ct = enemy.fly_back_tick
            if ct > c:
                c = ct
        self.fly_back_tick = c
        if self.fly_back_tick > 0:
            self.fly_back_tick -= 1
        self.rect = self.pos + [32,32]
