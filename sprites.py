import pygame
import os
from game_settings import *
import random

vec = pygame.math.Vector2
RED_SPRITE_IMAGE = pygame.image.load(os.path.join('Assets', 'sprites', 'sprite-red.png'))
RED_SPRITE = pygame.transform.scale(RED_SPRITE_IMAGE, (50, 50))
ORANGE_SPRITE_IMAGE = pygame.image.load(os.path.join('Assets', 'sprites', 'sprite-orange.png'))
ORANGE_SPRITE = pygame.transform.scale(ORANGE_SPRITE_IMAGE, (50, 50))
GREEN_SPRITE_IMAGE = pygame.image.load(os.path.join('Assets', 'sprites', 'sprite-green.png'))
GREEN_SPRITE = pygame.transform.scale(GREEN_SPRITE_IMAGE, (50, 50))
PURPLE_SPRITE_IMAGE = pygame.image.load(os.path.join('Assets', 'sprites', 'sprite-purple.png'))
PURPLE_SPRITE = pygame.transform.scale(PURPLE_SPRITE_IMAGE, (50, 50))


class Player(pygame.sprite.Sprite):
    def __init__(self, game, spawn_location, player_num, player_pos): # pass it game so that it can retrieve information about the surroundings
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.player_num = player_num
        self.player_pos = player_pos
        # self.image = RED_SPRITE_IMAGE
        if self.player_num == 1:
            self.image = RED_SPRITE
        elif self.player_num == 2:
            self.image = ORANGE_SPRITE
        elif self.player_num == 3:
            self.image = GREEN_SPRITE
        elif self.player_num == 4:
            self.image = PURPLE_SPRITE
        self.ammo_count = 0
        self.health = 20
        self.rect = self.image.get_rect()
        self.rect.center = (spawn_location)

        self.pos = vec(spawn_location) # has an x,y component represented in the vector
        self.vel = vec(0, 0)
        self.acc = vec(0,0)

    def jump(self):
        # check if allowed to jump: only if floor below
        self.rect.y += 1 # shift up and down while checking if floor in pixel below
        hits = pygame.sprite.spritecollide(self, self.game.all_platforms, False)
        pp_collide = self.game.player1.rect.colliderect(self.game.player2)
        self.rect.y -= 1 # without updating, this dopes not result in a visual effect
        if hits or pp_collide:  # only allow jump if hits has a collsion
            self.game.jump_sound.play()
            self.vel.y -= 14  # negative direction because it jumps toward 0

    def update(self):
        self.acc = vec(0, PLAYER_GRAVITY) # resets acceleration to 0 on update (stays at 0 if no keys pressed
        keys_pressed = pygame.key.get_pressed()
        if self.player_pos == 'left':
            if keys_pressed[pygame.K_a]:
                self.acc.x = -PLAYER_ACC
            if keys_pressed[pygame.K_d]:
                self.acc.x = PLAYER_ACC
        if self.player_pos == 'right':
            if keys_pressed[pygame.K_LEFT]:
                self.acc.x = -PLAYER_ACC
            if keys_pressed[pygame.K_RIGHT]:
                self.acc.x = PLAYER_ACC
        # if keys_pressed[pygame.K_w]:
        #     self.acc.y = -PLAYER_ACC

        self.acc.x += self.vel.x * PLAYER_FRICTION # deceleration force, caps speed naturally and stops when slowing
        self.vel += self.acc
        self.pos += self.vel + PLAYER_ACC * self.acc


        # wrap around sides of the screen
        if self.pos.x > RES_WIDTH - 20:
            self.pos.x = RES_WIDTH - 20
            self.vel.x = 0
        if self.pos.x < 20:
            self.pos.x = 20
            self.vel.x = 0

        self.rect.midbottom = self.pos  # mid bottom so on collision, the mid bottom is set on top

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):  # parameters: x and y coordinate, width, height
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(GRASS_GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, section):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        self.image.fill(GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.section = section
        self.counter = 0

    def move_cycle(self, section):
        if section == 'top':
            if self.counter in range(0, 300):
                pass
            elif self.counter in range(300, 324):
                self.rect.y -= 10  # open; pull up (24)
            elif self.counter in range(324, 624):
                pass
            elif self.counter in range(624, 648):
                self.rect.y += 10  # close; pull down
            else:
                self.counter = 0
        if section == 'bottom':
            if self.counter in range(0, 300):
                pass
            elif self.counter in range(300, 324):
                self.rect.y += 10  # close; pull down
            elif self.counter in range(324, 624):
                pass
            elif self.counter in range(624, 648):
                self.rect.y -= 10  # open; pull up
            else:
                self.counter = 0
        self.counter += 1

class AmmoBall(pygame.sprite.Sprite):
    def __init__(self, y, w, h, r, side):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((w, h))
        # if fill and color_key are the same color, the background will be transparent
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        self.color = GOLD
        pygame.draw.circle(self.image, self.color, (w//2, h//2), r) # width and height of hte Surface box
        self.rect = self.image.get_rect()
        self.counter = 0
        self.isFalling = False
        self.side = side
        self.y = y
        self.spawn_choices = []
        self.spawn_x = -5  # will be obvious if this does not get initiated
        if self.side == 'player1':
            self.spawn_choices = [0, 22, 44, 66, 88, 110, 132, 154, 176, 198, 220, 242, 264,
                                  286, 308, 330, 352]
            self.spawn_x = random.choice(self.spawn_choices)
        if self.side == 'player2':
            self.spawn_choices = [415, 437, 459, 481, 503, 525, 547, 569, 591, 613, 635, 657,
                                  679, 701, 723, 745, 767]
            self.spawn_x = random.choice(self.spawn_choices)
        self.rect.x = self.spawn_x
        self.rect.y = self.y

    def spawn(self):
        pass

    def update(self):
        if self.isFalling:
            self.rect.y += 3

class FiredBullet(pygame.sprite.Sprite):
    def __init__(self, game, player, direction):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.player = player
        self.image = pygame.Surface((25, 10))
        self.image.fill(GOLD)
        self.rect = self.image.get_rect()
        self.direction = direction
        if self.direction == 'right':
            self.rect.x = player.rect.x + 55
        if self.direction == 'left':
            self.rect.x = player.rect.x - 35
        self.rect.y = player.rect.y + 15


    def update(self):
        if self.direction == 'right':
            self.rect.x += 5
        if self.direction == 'left':
            self.rect.x -= 5
        if -25 > self.rect.x or self.rect.x > RES_WIDTH:
            self.kill()
            if self.player == self.game.player1:
                self.game.p1_fired_bullets.remove(self)
            if self.player == self.game.player2:
                self.game.p2_fired_bullets.remove(self)
