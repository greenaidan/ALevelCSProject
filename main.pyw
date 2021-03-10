import pygame, time, copy, random, math, save_mgnt

pygame.init()
pygame.display.set_caption('Alma Qabir')
icon = pygame.image.load("misc assets\logo.png")
pygame.display.set_icon(icon)

(width, height) = (768, 768)
screen = pygame.display.set_mode((width, height))
pygame.display.update()


tick = 1
clock = pygame.time.Clock()

save = save_mgnt.Save("1")


while True:
    for x in range(1):
        save.update(screen, tick) 
        tick += 1
        if (tick%60) == 0:
            print(clock.get_fps())
        
    pygame.display.update()
    clock.tick(60)
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save.force_save()
            pygame.quit()
            exit()
        
