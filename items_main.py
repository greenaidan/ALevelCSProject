import pygame, copy

def myround(x, base=5):
    return base * round(x/base)

def interact(check,blocks):
    for block in blocks:
        if (check[0]<block[0]+block[2])and(check[0]+check[2]>block[0])and (check[1]<block[1]+block[3])and(check[1]+check[3]>block[1]):
            return True
    return False

class Poof:
    def __init__(self, pos, blow_tick):
        self.type = "poof"
        self.pos = pos
        self.blow_tick = blow_tick
        self.image = pygame.image.load("misc_sprites/poof.png")
        self.image = pygame.transform.scale(self.image,(32, 32))
    def update(self, room, player):
        self.blow_tick -= 1
    def draw(self, screen):
        pixel_pos = [myround(x,4) for x in self.pos]
        screen.blit(self.image,pixel_pos)

class Coffin:
    def __init__(self, pos, room_pos, health, num_bombs):
        self.type = "coffin"
        self.pos = pos
        self.room_pos = room_pos
        self.health = health
        self.num_bombs = num_bombs
        self.image = pygame.image.load("misc_sprites/coffin.png")
        self.image = pygame.transform.scale(self.image,(64, 64))
        
    def draw(self, screen):
        pixel_pos = [myround(x,4) for x in self.pos]
        screen.blit(self.image,pixel_pos)

class Life_point_add:
    def __init__(self, pos, amount):
        self.pos = pos
        self.amount = amount
        self.type = "life_point_add"
        image = pygame.image.load("misc_sprites/life_point_add.png")
        image = pygame.transform.scale(image,(32, 32))
        self.image = image
        self.rect = self.pos+[32,32]
        
    def update(self, player):
        speed = 3
        diff = [self.pos[0]-player.pos[0], self.pos[1]-player.pos[1]]
        mag = (diff[0]**2 + diff[1]**2)**0.5
        diff = [(diff[0]/mag)*speed, (diff[1]/mag)*speed]
        self.pos[0]-=diff[0]
        self.pos[1]-=diff[1]
        self.rect = self.pos+[32,32]
        
    def draw(self, screen):
        pixel_pos = [myround(x,4) for x in self.pos]
        screen.blit(self.image, pixel_pos)
        

class gain:
    def __init__(self, gain, pos):
        self.gain = gain
        self.pos = pos
        self.rect = self.pos+[32,32]

    def draw(self, screen):
        pixel_pos = [myround(x,4) for x in self.pos]
        screen.blit(self.image,pixel_pos)

class Health_bottle(gain):
    def __init__(self, gain, pos):
        super().__init__(gain, pos)
        self.type = "health"
        image = pygame.image.load("misc_sprites/health_bottle.png")
        image = pygame.transform.scale(image,(32, 32))
        self.image = image



class Bomb_add(gain):
    def __init__(self, gain , pos):
        super().__init__(gain, pos)
        self.type = "bomb_add"
        image = pygame.image.load("misc_sprites/bomb_add.png")
        image = pygame.transform.scale(image,(32, 32))
        self.image = image
        

class Bomb:
    def __init__(self, pos):
        self.type = "bomb"
        self.radius = 1
        self.set_pos(pos)
        self.blow_tick = 60
        self.rect = self.pos+[64,64]
        self.bomb_off = False

    def set_pos(self, pos):
        temp_pos = [(pos[0]//64)*64,(pos[1]//64)*64]
        if pos[0]-temp_pos[0] > 32:
            temp_pos[0]+= 64
        if pos[1]-temp_pos[1] > 32:
            temp_pos[1]+= 64
        self.pos = temp_pos

    def update(self, room, player):
        self.blow_tick -= 1
        if self.blow_tick == 0:
            self.blow(room, player)
        
    def blow(self, room, player):
        pos_norm = [self.pos[0]//64, self.pos[1]//64]
        pos_start = [int(pos_norm[0]-self.radius), int(pos_norm[1]-self.radius)]
        for x in range (2*self.radius+1):
            for y in range(2*self.radius+1):
                try:
                    if room.tiles[pos_start[1]+y][pos_start[0]+x] == "tt":
                        room.tiles[pos_start[1]+y][pos_start[0]+x] = "ms"
                except:
                    room
        room.update_blocks()
        blow_rect = [self.pos[0]-64,self.pos[1]-64,192,192]
        for enemy in room.enemies:
            if interact(enemy.rect, [blow_rect]):
                enemy.health -= 3
                enemy.fly_back_tick = 9
        if interact(player.rect, [blow_rect]):
            player.health -= 4
            player.blood_tick = 15
        
    def draw(self, screen):
        if not self.bomb_off:
            name = "bomb"+str(4 - self.blow_tick//15)+".png"
            image = pygame.image.load("misc_sprites/"+name)
            bomb = pygame.transform.scale(image,(64, 64))
            screen.blit(bomb, self.pos)
        if self.blow_tick < 15:
            t = 4 - self.blow_tick//3
            name = "e"+str(t)+".png"
            image = pygame.image.load("misc_sprites/"+name)
            image = pygame.transform.scale(image,(192, 192))
            screen.blit(image, [self.pos[0]-64, self.pos[1]-64])
            
