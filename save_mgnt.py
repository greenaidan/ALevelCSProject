import pygame, time, copy, random, math
import room_main, player_main, text

class Save:
    def __init__(self, name):
        self.name = name
        self.player = player_main.Player(name)
        self.room = room_main.room(self.name,self.player.loc)
    def update(self, screen, tick):
        screen.fill([0]*3)
        keys_hold = pygame.key.get_pressed()
        if not keys_hold[pygame.K_m]:
            self.player.move(self.room, screen)
            self.room.move(self.player, screen, tick)
            
            self.room.draw(screen, tick)
            self.player.draw(screen, tick)
            self.player.draw_stats(screen)
            self.room.draw_items(screen)
            self.room.draw_enemies(screen, tick)
        else:
            self.player.draw_map(screen)
        if tick%120 == 0:
            self.room.save_room()
            self.player.save_player()
        if self.player.move_room:
            self.player.save_player()

        if self.player.dead:
            self.room.save_room()
            self.player.dead = False
            self.player.blood = []
            self.player.blood_tick = 0
            self.player.life_points_amount = 0
            if self.player.coffin != None:
                self.room.__init__(self.name, self.player.coffin.room_pos)
                self.player.health = self.player.coffin.health
                self.player.num_bombs = self.player.coffin.num_bombs
                self.player.loc = self.player.coffin.room_pos
                self.player.pos = self.player.coffin.pos
                self.player.coffin = None
                self.player.save_player()
            else:
                self.room.__init__(self.name, [0,0])
                self.player.health = 4
                self.player.num_bombs = 0
                self.player.loc = [0,0]
                self.player.pos = [100,100]
                self.player.coffin = None
                self.player.save_player()                
                
            
    def force_save(self):
        self.player.save_player()
        self.room.save_room()

            
        

