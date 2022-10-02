import pygame
import sys, random, math
from numpy import interp
from pymata4 import pymata4

pygame.init()

WIDTH = 800
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Title
pygame.display.set_caption('')
icon = pygame.image.load('data\player.png').convert_alpha()
pygame.display.set_icon(icon)


# stick arduino mapping
my_board = pymata4.Pymata4()
my_board.set_pin_mode_digital_input_pullup(2)
my_board.set_pin_mode_analog_input(0)
my_board.set_pin_mode_analog_input(1)

clock = pygame.time.Clock()
player_speed = 6

# Bacground
scroll = 0
def bacground(scroll):
    bg_img = pygame.image.load('data/background.jpg').convert_alpha()
    bg_height = bg_img.get_height()
    tiles = math.ceil(HEIGHT / bg_height) + 1
    for i in range(0, tiles):
        screen.blit(bg_img, (0, i * -bg_height + scroll))

#player location and sprites variables
playerX = 378
playerY = 650
sprites = []
current_sprite = 0
animation = False
#sound 
plane_sound = pygame.mixer.Sound('data\plane_sound.wav')


def player(x, y):
    #player sprites for animation loop
    pl_sprite01 = pygame.image.load('data\plane01.png').convert_alpha()
    pl_sprite02 = pygame.image.load('data\plane02.png').convert_alpha()
    pl_sprite03 = pygame.image.load('data\plane03.png').convert_alpha()
    pl_sprite04 = pygame.image.load('data\plane04.png').convert_alpha()

    sprites.extend((pl_sprite01, pl_sprite02, pl_sprite03, pl_sprite04))

    playerIcon = sprites[int(current_sprite)]
    position = playerIcon.get_rect(center=(x, y))



    wrap_around = False

    # off screen left
    if position[0] < 0:
        position.move_ip(WIDTH, 0)
        wrap_around = True
    # off screen right
    elif position[0] + playerIcon.get_width() > WIDTH:
        position.move_ip(-WIDTH, 0)
        wrap_around = True
    # off screen top
    elif position[1] < 0:
        position.move_ip(0, HEIGHT)
        wrap_around = True
    # off screen bottom
    elif position[1] + playerIcon.get_width() > HEIGHT:
        position.move_ip(0, -HEIGHT)
        wrap_around = True

    if wrap_around == True:
        screen.blit(playerIcon, position)

    position[0] %= WIDTH
    position[1] %= HEIGHT
    x %= WIDTH
    y %= HEIGHT


    screen.blit(playerIcon, position)

#enemy
enemyX = random.randint(0,800)
enemyY = random.randint(50,200)

enemyIcon = pygame.image.load('data\pumpkin.png').convert_alpha()
enemy_01 = enemyIcon.get_rect(center=(enemyX,enemyY))
enemy_movement_X = 2
enemy_movement_Y = 2

def enemy(x, y):
    screen.blit(enemyIcon, enemy_01)
    enemy_01.x = x
    enemy_01.y = y

#bullets variable
bullets = []
x_traject = []
counting = []
def shooting(): # shooting bullets and colision

    for i in range(0,len(bullets), 10):
        b_y = bullets[i] #taking Y position
        b_x = x_traject[i] #taking X position
        bullet = pygame.draw.circle(screen, (255,0,0), (b_x, b_y), radius=3)
        bullets[i] -= 5 # bullet speed

        #check colision and set enemy full visible
        if bullet.colliderect(enemy_01) == False:
            enemyIcon.set_alpha(255)

        #check colision, set enemy half visible and add hit
        if bullet.colliderect(enemy_01) == True:
            counting.append(1)
            enemyIcon.set_alpha(128)
            print(len(counting))

        #after few hits turn off enemy
        if len(counting) > 100:
            enemyIcon.fill((0, 0, 0, 0))
            counting.clear()

    if len(bullets) > 500: #clearing bullets from list
        del bullets[:150]
        del x_traject[:150]


while True:

    clock.tick(60)
    #print('FPS ' + str(int(clock.get_fps())))

    # BG image
    scroll += 0.8 #bacground speed
    bacground(scroll)
    if scroll > 1000:
        scroll = 0

    # reading arduino inputs
    sw, time_stamp = my_board.digital_read(2)
    vrx, time_stamp2 = my_board.analog_read(0)
    vry, time_stamp3 = my_board.analog_read(1)
    #pygame event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # stick mapping to get more accurate movement
    range_vrx = interp(vrx, [0, 1023], [0, 128])
    range_vry = interp(vry, [0, 1024], [0, 128])


    # movement player
    if sw == 0:
        bullets.append(playerY - 36) #setting of current Y position for bullet and offset to plane's edge
        x_traject.append(playerX) # X position for bullet

    # diagonall movement
    elif range_vrx > 64 and range_vry < 63:
        playerX += player_speed / 2
        playerY -= player_speed / 2
    elif range_vrx < 62 and range_vry < 63:
        playerX -= player_speed / 2
        playerY -= player_speed / 2
    elif range_vrx < 62 and range_vry > 65:
        playerX -= player_speed / 2
        playerY += player_speed / 2
    elif range_vrx > 64 and range_vry > 65:
        playerX += player_speed / 2
        playerY += player_speed / 2
    # player movement straight
    elif range_vrx > 64:
        playerX += 5
    elif range_vrx < 63:
        playerX -= 5
    elif range_vry < 64:
        playerY -= 5
    elif range_vry > 65:
        playerY += 5

    # player location reading
    player(playerX, playerY)
    plane_sound.play()

    # reseting position for wrap action
    if playerX < 0:
        playerX = 800
    elif playerX > 800:
        playerX = 0
    elif playerY < 0:
        playerY = 800
    elif playerY > 800:
        playerY = 0
#shooting
    if len(bullets):
        shooting()

#animation player
    animation = True
    if animation:
        current_sprite += 1
        if int(current_sprite) > len(sprites):
            current_sprite = 0
            animation = False

    # enemy movement
    enemyX += enemy_movement_X
    # frame enemy movement
    if enemyX <= 60:
        enemy_movement_X = random.randint(2, 5)
    elif enemyX >= 690:
        enemy_movement_X = random.randint(2, 5) * -1
    # enemy postion
    enemy(enemyX, enemyY)

    pygame.display.update()
