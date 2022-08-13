import pygame
import os, sys
from pygame.locals import *
APP_FOLDER = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(APP_FOLDER)
pygame.init()
pygame.mixer.init()

#Game Sounds
hit = pygame.mixer.Sound("hit.wav")
music = pygame.mixer.music.load("Alla-Turca.mp3") 
pygame.mixer.music.play(-1)

screen_width = 1200
screen_height = 700
background = (0, 0, 0)
fps = 105
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Breakout')

#Block colors
b_red = (205, 0, 0)
b_green = (0, 210, 0)
b_blue = (0, 0, 232)

#Text
txt_col = (255, 255, 255)
font = pygame.font.SysFont('Constantia', 30)

#Show text on the screen   
def show_text(text, font, txt_col, x, y):
    screen.blit(font.render(text, True, txt_col), (x,y))

#Paddle colors
paddle_col = (255, 255, 255)
paddle_outline = (200, 100, 100)

#Rows and Cols
cols = screen_width // 100
rows = 7
ball_exists = False
game_over = 0


#brick wall class
class wall():
    def __init__(self):
        self.width = screen_width // cols
        self.height = 35

    def create_wall(self):
        self.blocks = [] 
        #define an empty list for an individual block
        block_individual = []
        for row in range(rows):
            #reset the block row list
            block_row = []
            #iterate through each column in that row
            for col in range(cols):
                #generate x and y positions for each block and create a rectangle from that
                block_x = col * self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x, block_y, self.width, self.height)
                #assign block strength based on row
                if row < 2:
                    strength = 3
                elif row < 5:
                    strength = 2
                else:
                    strength = 1
                #create a list at this point to store the rect and color data
                block_individual = [rect, strength]
                block_row.append(block_individual)
            self.blocks.append(block_row)

    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                #assign a color based on block strength
                if block[1] == 3:
                    block_col = b_blue
                elif block[1] == 2:
                    block_col = b_green
                elif block[1] == 1:
                    block_col = b_red
                pygame.draw.rect(screen, block_col, block[0])
                pygame.draw.rect(screen, background, (block[0]), 1)

#paddle class
class paddle():
    def __init__(self):
        self.height = 20
        self.width = int(screen_width / cols)
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = screen_height - (self.height * 2)
        self.speed = 10
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0

    def reset(self):
        self.__init__()

    def move(self):
        #reset movement direction
        self.direction = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += self.speed
            self.direction = 1
    
    def draw(self):
        pygame.draw.rect(screen, paddle_col, self.rect)
        pygame.draw.rect(screen, paddle_outline, self.rect, 3)


class ball():
    def __init__(self, x, y):
        self.ball_rad = 10
        self.x = x - self.ball_rad
        self.y = y
        self.rect = Rect(self.x, self.y, self.ball_rad * 2, self.ball_rad * 2)
        self.speed_x = 4
        self.speed_y = -4
        self.max_speed = 5
        self.game_over = 0

    def reset(self, x, y):
        self.__init__(x, y)
    
    def move(self):
        #threshold for collision
        tolerance = 5
        row_count = 0
        wall_destroyed = 1
        for row in wall.blocks:
            bl_count = 0
            for bl in row:
                #checking collision
                if self.rect.colliderect(bl[0]):
                    hit.play()
                    #from above
                    if abs(self.rect.bottom - bl[0].top) < tolerance and self.speed_y > 0:
                        self.speed_y *= -1
                    #from below
                    if abs(self.rect.top - bl[0].bottom) < tolerance and self.speed_y < 0:
                        self.speed_y *= -1
                    #from left
                    if abs(self.rect.right - bl[0].left) < tolerance and self.speed_x > 0:
                        self.speed_x *= -1
                    #from below
                    if abs(self.rect.left - bl[0].right) < tolerance and self.speed_x < 0:
                        self.speed_x *= -1

                    # decreasing block strength for each collision
                    if wall.blocks[row_count][bl_count][1] > 1:
                        wall.blocks[row_count][bl_count][1] -= 1
                    else:
                        wall.blocks[row_count][bl_count][0] = (0, 0, 0, 0) #no properties in the rectangle

                #check if there are still blocks left (wall is not destroyed)

                if wall.blocks[row_count][bl_count][0] != (0, 0, 0, 0):
                    wall_destroyed = 0
                #increasing bl counter
                bl_count += 1
            row_count += 1

            #finally checking if the wall exists

            if wall_destroyed == 1:
                self.game_over = 1

        #check collisions with walls
        if self.rect.left < 0  or self.rect.right > screen_width:
            self.speed_x *= -1 #change direction

        #check collisions with top and bottom
        if self.rect.top < 0:
            self.speed_y *= -1
        if self.rect.bottom > screen_height:
            self.game_over = -1
        
        #check paddle collision
        if self.rect.colliderect(player_paddle):
            #top collision
            if abs(self.rect.bottom - player_paddle.rect.top) < tolerance and self.speed_y > 0:
                self.speed_y *= -1
                self.speed_x += player_paddle.direction
                if self.speed_x > self.max_speed:
                    self.speed_x = self.max_speed
                elif self.speed_x < 0 and self.speed_x < -self.max_speed:
                    self.speed_x = -self.max_speed
            else:
                self.speed_x *= -1


        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.game_over

    def draw(self):
        pygame.draw.circle(screen, paddle_col, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
        pygame.draw.circle(screen, paddle_outline, (self.rect.x + self.ball_rad, self.rect.y + self.ball_rad), self.ball_rad)
    

#create wall
wall = wall()
wall.create_wall()

#create paddle
player_paddle = paddle()

#create ball
game_ball = ball(player_paddle.x + player_paddle.width // 2, player_paddle.y - player_paddle.height)

run = True
while run:
    clock.tick(fps)
    screen.fill(background)

    #drawing and motion
    game_wall = wall.draw_wall()
    player_paddle.draw()
    game_ball.draw()

    if ball_exists:
        player_paddle.move()
        game_over = game_ball.move()
        if game_over != 0:
            ball_exists = False
            game_ball.reset(player_paddle.x + player_paddle.width // 2, player_paddle.y - player_paddle.height)
            player_paddle.reset()
    
    #info for the player
    if not ball_exists:
        if pygame.key.get_pressed()[pygame.K_LEFT]  and player_paddle.rect.left > 0:
                game_ball.rect.x -= player_paddle.speed
                game_ball.direction = -1
        elif pygame.key.get_pressed()[pygame.K_RIGHT] and player_paddle.rect.right < screen_width:
                game_ball.rect.x += player_paddle.speed
                game_ball.direction = 1
        player_paddle.move()

        if game_over == 0:
            show_text("Use the <- arrows -> and Press [SPACE] to Start", font, txt_col, 300, screen_height // 2 + 100)
        elif game_over == 1:
            show_text("YOU WON", font, txt_col, 530, screen_height // 2 + 50)
            show_text("Click Anywhere to Start", font, txt_col, 460, screen_height // 2 + 100)
            
        elif game_over == -1:
            show_text("YOU LOST", font, txt_col, 530, screen_height // 2 + 50)
            show_text("Click Anywhere to Start", font, txt_col, 460, screen_height // 2 + 100)
            

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if pygame.key.get_pressed()[pygame.K_SPACE] and ball_exists == False:                
            ball_exists = True
            paddle_col = (255, 255, 255)
            paddle_outline = (200, 100, 100)
            wall.create_wall()
    
    pygame.display.update()

pygame.quit()