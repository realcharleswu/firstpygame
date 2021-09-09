import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time
import random

import pygame.sprite

from game_settings import *
from sprites import *

class Game:

    def __init__(self):
        # Initialize game variables

        pygame.init()  # initializes pygame
        pygame.mixer.init()  # handles sound and music

        self.WINDOW = pygame.display.set_mode((RES_WIDTH, RES_HEIGHT))
        pygame.display.set_caption('Wall Warriors')
        self.game_clock = pygame.time.Clock()
        self.exit_early = False
        self.running = True
        self.load_data()  # load in images and sounds in a format that pygame can use

    def load_data(self):
        self.jump_sound = pygame.mixer.Sound(os.path.join('Sounds', 'player-jump.wav'))
        self.collect_sound = pygame.mixer.Sound(os.path.join('Sounds', 'collect-ball-sound.wav'))
        self.fire_sound = pygame.mixer.Sound(os.path.join('Sounds', 'player-fire-sound.wav'))
        self.player_struck = pygame.mixer.Sound(os.path.join('Sounds', 'player-got-hit.wav'))
        self.background_music = pygame.mixer.Sound(os.path.join('Sounds', 'background-music.mp3'))

        self.p1_control_graphic_image = pygame.image.load(os.path.join('Assets', 'graphics', 'controls-graphic-p1.png'))
        self.p2_control_graphic_image = pygame.image.load(os.path.join('Assets', 'graphics', 'controls-graphic-p2.png'))
        self.p1_control_graphic = pygame.transform.smoothscale(self.p1_control_graphic_image, (200, 267))
        self.p2_control_graphic = pygame.transform.smoothscale(self.p2_control_graphic_image, (200, 267))

        RED_SPRITE_IMAGE = pygame.image.load(os.path.join('Assets', 'sprites', 'sprite-red.png'))
        self.RED_SPRITE = pygame.transform.scale(RED_SPRITE_IMAGE, (50, 50))
        ORANGE_SPRITE_IMAGE = pygame.image.load(os.path.join('Assets', 'sprites', 'sprite-orange.png'))
        self.ORANGE_SPRITE = pygame.transform.scale(ORANGE_SPRITE_IMAGE, (50, 50))
        GREEN_SPRITE_IMAGE = pygame.image.load(os.path.join('Assets', 'sprites', 'sprite-green.png'))
        self.GREEN_SPRITE = pygame.transform.scale(GREEN_SPRITE_IMAGE, (50, 50))
        PURPLE_SPRITE_IMAGE = pygame.image.load(os.path.join('Assets', 'sprites', 'sprite-purple.png'))
        self.PURPLE_SPRITE = pygame.transform.scale(PURPLE_SPRITE_IMAGE, (50, 50))

    def run(self):
        # Game loop
        self.playing = True
        while self.playing:
            self.game_clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def new(self):
        # start a new game

        self.all_sprites = pygame.sprite.Group()
        self.all_platforms = pygame.sprite.Group()
        self.all_ammo = pygame.sprite.Group()

        self.player1 = Player(self, (RES_WIDTH/4, RES_HEIGHT/4), self.player1_sprite_number, 'left') # create new player
        self.all_sprites.add(self.player1) #add to main sprite group

        self.player2 = Player(self, (3 * RES_WIDTH / 4, RES_HEIGHT/4), self.player2_sprite_number, 'right')
        self.all_sprites.add(self.player2)

        floor = Platform(0, RES_HEIGHT - 50, RES_WIDTH, 50)
        self.all_sprites.add(floor)
        self.all_platforms.add(floor)

        p1_platform1 = Platform(20, 250, 80, 20)
        self.all_sprites.add(p1_platform1)
        self.all_platforms.add(p1_platform1)

        p1_platform2 = Platform(240, 250, 80, 20)
        self.all_sprites.add(p1_platform2)
        self.all_platforms.add(p1_platform2)

        p1_platform3 = Platform(134, 85, 80, 20)
        self.all_sprites.add(p1_platform3)
        self.all_platforms.add(p1_platform3)

        p2_platform1 = Platform(470, 250, 80, 20)
        self.all_sprites.add(p2_platform1)
        self.all_platforms.add(p2_platform1)

        p2_platform2 = Platform(700, 250, 80, 20)
        self.all_sprites.add(p2_platform2)
        self.all_platforms.add(p2_platform2)

        p2_platform3 = Platform(563, 85, 80, 20)
        self.all_sprites.add(p2_platform3)
        self.all_platforms.add(p2_platform3)

        self.top_wall = Wall(RES_WIDTH/2 - 15, 0, 30, RES_HEIGHT/2, 'top')
        self.all_platforms.add(self.top_wall)
        self.all_sprites.add(self.top_wall)

        self.bottom_wall = Wall(RES_WIDTH / 2 - 15, RES_HEIGHT/2, 30, RES_HEIGHT / 2, 'bottom')
        self.all_platforms.add(self.bottom_wall)
        self.all_sprites.add(self.bottom_wall)

        self.player1_ammo_list = []  # stores potential player1 side falling ammo (left)
        self.player2_ammo_list = []  # stores potential player1 side falling ammo (left)
        self.initialize_ammo()
        self.first_initialize = True

        self.all_fired_bullets = pygame.sprite.Group()
        self.p1_fired_bullets = []
        self.p2_fired_bullets = []

        self.p1_fire_last = pygame.time.get_ticks()
        self.p2_fire_last = pygame.time.get_ticks()
        self.fire_cooldown = 180

        self.wall_counter = 0
        self.combat_mode = False #start off collection

        self.winner = -1  # obvious placeholder value

        self.P1_HIT = pygame.USEREVENT + 1
        self.P2_HIT = pygame.USEREVENT + 2

        self.collect_sound.set_volume(1.1)
        self.jump_sound.set_volume(0.5)
        self.fire_sound.set_volume(0.3)
        self.background_music.set_volume(0.45)
        self.background_music.play(-1)

        self.run()

    def initialize_ammo(self):
        self.ammo1 = AmmoBall(20, 20, 20, 10, 'player1')
        self.ammo2 = AmmoBall(20, 20, 20, 10, 'player1')
        self.ammo3 = AmmoBall(25, 20, 20, 10, 'player1')
        self.ammo4 = AmmoBall(20, 20, 20, 10, 'player1')
        self.ammo5 = AmmoBall(20, 20, 20, 10, 'player1')

        self.ammo6 = AmmoBall(20, 20, 20, 10, 'player2')
        self.ammo7 = AmmoBall(20, 20, 20, 10, 'player2')
        self.ammo8 = AmmoBall(20, 20, 20, 10, 'player2')
        self.ammo9 = AmmoBall(20, 20, 20, 10, 'player2')
        self.ammo10 = AmmoBall(20, 20, 20, 10, 'player2')

        self.player1_ammo_list = [self.ammo1, self.ammo2, self.ammo3, self.ammo4, self.ammo5]
        self.player2_ammo_list = [self.ammo6, self.ammo7, self.ammo8, self.ammo9, self.ammo10]
        # self.ammo2, self.ammo3, self.ammo4, self.ammo5, self.ammo6,
        #              self.ammo7, self.ammo8, self.ammo9, self.ammo10, self.ammo11, self.ammo12,
        #              self.ammo13, self.ammo14, self.ammo15, self.ammo16, self.ammo17]
        self.all_sprites.add(self.ammo1, self.ammo2, self.ammo3, self.ammo4,
                             self.ammo5, self.ammo6, self.ammo7, self.ammo8, self.ammo9, self.ammo10)
        self.all_ammo.add(self.ammo1, self.ammo2, self.ammo3, self.ammo4,
                          self.ammo5, self.ammo6, self.ammo7, self.ammo8, self.ammo9, self.ammo10)

    def despawn_ammo(self):
        for ammo in self.all_ammo:
            ammo.kill()
        self.player1_ammo_list.clear()
        self.player2_ammo_list.clear()

    def ammo_respawner(self):
        for ammo in self.all_ammo:
            if ammo.rect.colliderect(self.player1):
                self.player1.ammo_count += 1
                self.collect_sound.play()
                ammo.kill()  # Kill removes all traces of the ammo
                if ammo.side == 'player1': #left side of the screen
                    new_ammo = AmmoBall(RES_HEIGHT / 4, 20, 20, 10, 'player1')  # prepare new one to be dropped
                    self.player1_ammo_list.remove(ammo)  # remove from the list of current falling ammo
                    self.player1_ammo_list.append(new_ammo)  # add new ammo to the list
                    self.all_ammo.add(new_ammo)
                    self.all_sprites.add(new_ammo)  # update sprite groups, all and ammo
                elif ammo.side == 'player2': #left side of the screen
                    new_ammo = AmmoBall(RES_HEIGHT / 4, 20, 20, 10, 'player2')  # prepare new one to be dropped
                    self.player2_ammo_list.remove(ammo)  # remove from the list of current falling ammo
                    self.player2_ammo_list.append(new_ammo)  # add new ammo to the list
                    self.all_ammo.add(new_ammo)
                    self.all_sprites.add(new_ammo)  # update sprite groups, all and ammo

            elif ammo.rect.colliderect(self.player2):
                self.player2.ammo_count += 1
                self.collect_sound.play()
                ammo.kill()  # Kill removes all traces of the ammo
                if ammo.side == 'player1':  # left side of the screen
                    new_ammo = AmmoBall(RES_HEIGHT / 4, 20, 20, 10, 'player1')  # prepare new one to be dropped
                    self.player1_ammo_list.remove(ammo)  # remove from the list of current falling ammo
                    self.player1_ammo_list.append(new_ammo)  # add new ammo to the list
                    self.all_ammo.add(new_ammo)
                    self.all_sprites.add(new_ammo)  # update sprite groups, all and ammo
                elif ammo.side == 'player2':  # left side of the screen
                    new_ammo = AmmoBall(RES_HEIGHT / 4, 20, 20, 10, 'player2')  # prepare new one to be dropped
                    self.player2_ammo_list.remove(ammo)  # remove from the list of current falling ammo
                    self.player2_ammo_list.append(new_ammo)  # add new ammo to the list
                    self.all_ammo.add(new_ammo)
                    self.all_sprites.add(new_ammo)  # update sprite groups, all and ammo

            if ammo.rect.x < RES_WIDTH/2 and ammo.rect.y > RES_HEIGHT-50:  # off screen, side specific
                ammo.kill()
                new_ammo = AmmoBall(RES_HEIGHT / 4, 20, 20, 10, 'player1')  # prepare new one to be dropped
                self.player1_ammo_list.remove(ammo)  # remove from the list of current falling ammo
                self.player1_ammo_list.append(new_ammo)  # add new ammo to the list
                self.all_ammo.add(new_ammo)
                self.all_sprites.add(new_ammo)  # update sprite groups, all and ammo
            if ammo.rect.x > RES_WIDTH/2 and ammo.rect.y > RES_HEIGHT-50:  # off screen, side specific
                ammo.kill()
                new_ammo = AmmoBall(RES_HEIGHT / 4, 20, 20, 10, 'player2')  # prepare new one to be dropped
                self.player2_ammo_list.remove(ammo)  # remove from the list of current falling ammo
                self.player2_ammo_list.append(new_ammo)  # add new ammo to the list
                self.all_ammo.add(new_ammo)
                self.all_sprites.add(new_ammo)  # update sprite groups, all and ammo

    def ammo_random_chooser(self):
        if not self.combat_mode:
            p1_ammo_handler = random.random()
            if p1_ammo_handler < 0.9:  # 5% chance to fall
                ammo_index = random.randint(0, len(self.player1_ammo_list)-1)
                self.player1_ammo_list[ammo_index].isFalling = True
            p2_ammo_handler = random.random()
            if p2_ammo_handler < 0.9:  # 5% chance to fall
                ammo_index = random.randint(0, len(self.player2_ammo_list) - 1)
                self.player2_ammo_list[ammo_index].isFalling = True


    def ammo_header_draw(self):
        myfont = pygame.font.SysFont('Arial Rounded', 18)
        header = "Ammo"
        spaces = '                                                                       '
        ammo_string = header + spaces + header
        text = myfont.render(ammo_string, True, BLACK)
        self.WINDOW.blit(text, (100, 3))

    def current_p1ammo_text_draw(self):
        myfont = pygame.font.SysFont('Arial', 45)
        ammo_text = str(self.player1.ammo_count)
        text = myfont.render(ammo_text, True, BLACK)
        self.WINDOW.blit(text, (112, 15))

    def current_p2ammo_text_draw(self):
        myfont = pygame.font.SysFont('Arial', 45)
        ammo_text = str(self.player2.ammo_count)
        text = myfont.render(ammo_text, True, BLACK)
        self.WINDOW.blit(text, (522, 15))

    def health_header_draw(self):
        myfont = pygame.font.SysFont('Arial Rounded', 18)
        header = 'Health'
        spaces = '                                                                       '
        health_text = header + spaces + header
        text = myfont.render(health_text, True, BLACK)
        self.WINDOW.blit(text, (3, 2))

    def current_p1health_draw(self):
        myfont = pygame.font.SysFont('Arial', 44)
        health_text = str(self.player1.health)
        text = myfont.render(health_text, True, BLACK)
        self.WINDOW.blit(text, (3, 15))

    def current_p2health_draw(self):
        myfont = pygame.font.SysFont('Arial', 44)
        health_text = str(self.player2.health)
        text = myfont.render(health_text, True, BLACK)
        self.WINDOW.blit(text, (417, 15))

    def handle_player_plat_collisions(self):
        collision_tolerance = 20  # tolerance since pixel precise collision not possible
        # a group that tracks collisions, boolean param indicates to delete on collision or not
        player1_hits = pygame.sprite.spritecollide(self.player1, self.all_platforms, False)
        if player1_hits:
            # FLOOR COLLIDE
            if abs(self.player1.rect.bottom - player1_hits[0].rect.top) < collision_tolerance:
                self.player1.pos.y = player1_hits[0].rect.top  # set player position to top of the platform they fall on
                self.player1.vel.y = 0  # sets velocity to 0, or else keeps falling due to constant gravity
                self.player1.rect.midbottom = self.player1.pos  # prevents shaking; corrects player pos on collide
            # CEILING COLLIDE
            elif abs(self.player1.rect.top - player1_hits[0].rect.bottom) < collision_tolerance:
                self.player1.pos.y = player1_hits[
                                         0].rect.bottom + 50  # +50 is due to the position being based on sprite bottom
                self.player1.vel.y = 0  # sets velocity to 0 to initiate falling, no need to correct for shaking
            # GOING LEFT COLLIDE
            elif abs(self.player1.rect.left - player1_hits[0].rect.right) < collision_tolerance:
                self.player1.pos.x = player1_hits[0].rect.right + 25  # +25 since pos is midbottom
                self.player1.vel.x = 0  # sets velocity to 0 to initiate falling, no need to correct for shaking
            # GOING RIGHT COLLIDE
            elif abs(self.player1.rect.right - player1_hits[0].rect.left) < collision_tolerance:
                self.player1.pos.x = player1_hits[0].rect.left - 25  # -25 since pos it midbottom
                self.player1.vel.x = 0  # sets velocity to 0 to initiate falling, no need to correct for shaking

        player2_hits = pygame.sprite.spritecollide(self.player2, self.all_platforms, False)
        if player2_hits:
            # FLOOR COLLIDE
            if abs(self.player2.rect.bottom - player2_hits[0].rect.top) < collision_tolerance:
                self.player2.pos.y = player2_hits[0].rect.top  # set player position to top of the platform they fall on
                self.player2.vel.y = 0  # sets velocity to 0, or else keeps falling due to constant gravity
                self.player2.rect.midbottom = self.player2.pos  # prevents shaking; corrects player pos on collide
            # CEILING COLLIDE
            elif abs(self.player2.rect.top - player2_hits[0].rect.bottom) < collision_tolerance:
                self.player2.pos.y = player2_hits[0].rect.bottom + 50  # +50 is due to the position being based on sprite bottom
                self.player2.vel.y = 0  # sets velocity to 0 to initiate falling, no need to correct for shaking
            # GOING LEFT COLLIDE
            elif abs(self.player2.rect.left - player2_hits[0].rect.right) < collision_tolerance:
                self.player2.pos.x = player2_hits[0].rect.right + 25  # +25 since pos is midbottom
                self.player2.vel.x = 0  # sets velocity to 0 to initiate falling, no need to correct for shaking
            # GOING RIGHT COLLIDE
            elif abs(self.player2.rect.right - player2_hits[0].rect.left) < collision_tolerance:
                self.player2.pos.x = player2_hits[0].rect.left - 25  # -25 since pos it midbottom
                self.player2.vel.x = 0  # sets velocity to 0 to initiate falling, no need to correct for shaking

    def handle_player_player_collisions(self):
        if self.player1.rect.colliderect(self.player2): # spritecollide needs groups
            # Player1 going right, player 2 going left
            if abs(self.player1.rect.right - self.player2.rect.left) < 15:
                self.player1.vel.x *= -3
                self.player2.vel.x *= -3
            if abs(self.player1.rect.left - self.player2.rect.right) < 15:
                self.player1.vel.x *= -3
                self.player2.vel.x *= -3
            if abs(self.player1.rect.bottom - self.player2.rect.top) < 20:
                if self.player1.vel.y < 4: # if player keeps bouncing, will slow to slip past tolerance
                    self.player1.vel.y += 3 #adds a small jump when its too slow
                self.player1.vel.y *= -1
                self.player2.vel.y *= -1
            if abs(self.player1.rect.top - self.player2.rect.bottom) < 20:
                if self.player2.vel.y < 4:
                    self.player2.vel.y += 3
                self.player1.vel.y *= -1
                self.player2.vel.y *= -1

    def player1_fire_bullet(self, direction):
        p1_fire_now = pygame.time.get_ticks()
        if self.combat_mode:
            if self.player1.ammo_count > 0 and (p1_fire_now - self.p1_fire_last) > self.fire_cooldown:
                if direction == 'left':
                    self.fire_sound.play()
                    p1_Bullet = FiredBullet(self, self.player1, 'left')
                    self.player1.ammo_count -= 1
                    self.p1_fire_last = pygame.time.get_ticks()
                    self.p1_fired_bullets.append(p1_Bullet)
                    self.all_fired_bullets.add(p1_Bullet)
                    self.all_sprites.add(p1_Bullet)
                if direction == 'right':
                    self.fire_sound.play()
                    p1_Bullet = FiredBullet(self, self.player1, 'right')
                    self.player1.ammo_count -= 1
                    self.p1_fire_last = pygame.time.get_ticks()
                    self.p1_fired_bullets.append(p1_Bullet)
                    self.all_fired_bullets.add(p1_Bullet)
                    self.all_sprites.add(p1_Bullet)

    def player2_fire_bullet(self, direction):
        p2_fire_now = pygame.time.get_ticks()
        if self.combat_mode:
            if self.player2.ammo_count > 0 and (p2_fire_now - self.p2_fire_last) > self.fire_cooldown:
                if direction == 'left':
                    self.fire_sound.play()
                    p2_Bullet = FiredBullet(self, self.player2, 'left')
                    self.player2.ammo_count -= 1
                    self.p2_fire_last = pygame.time.get_ticks()
                    self.p2_fired_bullets.append(p2_Bullet)
                    self.all_fired_bullets.add(p2_Bullet)
                    self.all_sprites.add(p2_Bullet)
                if direction == 'right':
                    self.fire_sound.play()
                    p2_Bullet = FiredBullet(self, self.player2, 'right')
                    self.player2.ammo_count -= 1
                    self.p2_fire_last = pygame.time.get_ticks()
                    self.p2_fired_bullets.append(p2_Bullet)
                    self.all_fired_bullets.add(p2_Bullet)
                    self.all_sprites.add(p2_Bullet)

    def handle_player_bullet_collisions(self):
        player1_bullet_hits = pygame.sprite.spritecollide(self.player1, self.all_fired_bullets, True)
        if player1_bullet_hits:
            self.player1.health -= 1
            self.p2_fired_bullets.remove(player1_bullet_hits[0])
            pygame.event.post(pygame.event.Event(self.P1_HIT))
        player2_bullet_hits = pygame.sprite.spritecollide(self.player2, self.all_fired_bullets, True)
        if player2_bullet_hits:
            self.player2.health -= 1
            self.p1_fired_bullets.remove(player2_bullet_hits[0])
            pygame.event.post(pygame.event.Event(self.P2_HIT))

    def handle_bullet_wall_collisions(self):
        for bullet in self.all_fired_bullets:
            if bullet.rect.colliderect(self.top_wall) or bullet.rect.colliderect(self.bottom_wall):
                if bullet.player == self.player1:
                    self.p1_fired_bullets.remove(bullet)
                if bullet.player == self.player2:
                    self.p2_fired_bullets.remove(bullet)
                bullet.kill()

    def combat_cycle(self):
        if self.wall_counter in range(0, 360): # collect; closed
            if self.wall_counter == 1:
                if not self.first_initialize:
                    self.initialize_ammo()
                    self.combat_mode = False
                if self.first_initialize:
                    self.first_initialize = False
        elif self.wall_counter in range(360, 384): # open door
            self.top_wall.rect.y -= 10  # open; pull up (24)
            self.bottom_wall.rect.y += 10
            self.combat_mode = True
        elif self.wall_counter == 384:
            self.despawn_ammo()
        elif self.wall_counter in range(385, 865): #fight
            self.combat_mode = True
        elif self.wall_counter in range(865, 889): #closing
            self.top_wall.rect.y += 10  # close; pull down
            self.bottom_wall.rect.y -= 10
        else:
            self.wall_counter = 0
        self.wall_counter += 1

    def check_who_won(self):
        if self.player1.health <= 0:
            self.winner = self.player2
            self.playing = False
            self.background_music.stop()
        elif self.player2.health <= 0:
            self.winner = self.player1
            self.playing = False
            self.background_music.stop()

    def update(self):
        # Update
        self.all_sprites.update()
        self.all_platforms.update()
        self.all_ammo.update()
        self.check_who_won()
        self.combat_cycle()
        self.handle_player_plat_collisions()
        self.handle_player_player_collisions()
        self.handle_bullet_wall_collisions()
        self.handle_player_bullet_collisions()
        self.ammo_random_chooser()
        self.ammo_respawner()


    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
                self.exit_early = True
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.player1.jump()
                if event.key == pygame.K_UP:
                    self.player2.jump()
                if event.key == pygame.K_f:
                    self.player1_fire_bullet('left')
                if event.key == pygame.K_g:
                    self.player1_fire_bullet('right')
                if event.key == pygame.K_COMMA:
                    self.player2_fire_bullet('left')
                if event.key == pygame.K_PERIOD:
                    self.player2_fire_bullet('right')
            if event.type == self.P1_HIT:
                self.player_struck.play()
            if event.type == self.P2_HIT:
                self.player_struck.play()



    def draw(self):
        # Render/Draw
        self.WINDOW.fill(SKY_BLUE)
        self.all_sprites.draw(self.WINDOW)
        self.ammo_header_draw()
        self.current_p1ammo_text_draw()
        self.current_p2ammo_text_draw()
        self.health_header_draw()
        self.current_p1health_draw()
        self.current_p2health_draw()
        pygame.display.flip()
    def display_start_screen(self):
        self.WINDOW.fill(SKY_BLUE)
        myfont = pygame.font.SysFont('Arial Rounded', 35)
        myfont.bold = True
        game_title = myfont.render('Wall Warriors', True, (255, 127, 80))
        self.WINDOW.blit(game_title, (265, 150))
        start_button = pygame.rect.Rect(RES_WIDTH/2-110, RES_HEIGHT/2, 220, 60)
        pygame.draw.rect(self.WINDOW, (41, 110, 1), start_button)

        self.WINDOW.blit(self.p1_control_graphic, (100, 250))
        self.WINDOW.blit(self.p2_control_graphic, (510, 250))

        start_font = pygame.font.SysFont('Arial Black', 30)
        start_text = start_font.render('START', True, WHITE)
        self.WINDOW.blit(start_text, (RES_WIDTH/2-55, RES_HEIGHT/2+5))
        pygame.display.flip()
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    self.exit_early = True
                    self.running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()

                    if start_button.collidepoint(mouse_pos):
                        done = True

    def display_char_selection(self):
        if not self.exit_early:
            self.player1_choose = True #if False, player2 chooses
            self.WINDOW.fill(SKY_BLUE)
            display_group = pygame.sprite.Group()

            myfont = pygame.font.SysFont('Arial Black', 36)
            myfont.bold = True
            p1_select_text = myfont.render('Player 1, select your avatar!', True, BLACK)
            p2_select_text = myfont.render('Player 2, select your avatar!', True, BLACK)
            self.WINDOW.blit(p1_select_text, (80, 100))

            RED_SPRITE_DISPLAY = pygame.sprite.Sprite()
            RED_SPRITE_DISPLAY.image = pygame.transform.scale(RED_SPRITE_IMAGE, (100, 100))
            RED_SPRITE_DISPLAY.rect = RED_SPRITE_DISPLAY.image.get_rect()
            RED_SPRITE_DISPLAY.rect.center = (175, 2*RES_HEIGHT//3)
            display_group.add(RED_SPRITE_DISPLAY)

            GREEN_SPRITE_DISPLAY = pygame.sprite.Sprite()
            GREEN_SPRITE_DISPLAY.image = pygame.transform.scale(GREEN_SPRITE_IMAGE, (100, 100))
            GREEN_SPRITE_DISPLAY.rect = GREEN_SPRITE_DISPLAY.image.get_rect()
            GREEN_SPRITE_DISPLAY.rect.center = (325, 2 * RES_HEIGHT // 3)
            display_group.add(GREEN_SPRITE_DISPLAY)

            ORANGE_SPRITE_DISPLAY = pygame.sprite.Sprite()
            ORANGE_SPRITE_DISPLAY.image = pygame.transform.scale(ORANGE_SPRITE_IMAGE, (100, 100))
            ORANGE_SPRITE_DISPLAY.rect = ORANGE_SPRITE_DISPLAY.image.get_rect()
            ORANGE_SPRITE_DISPLAY.rect.center = (475, 2 * RES_HEIGHT // 3)
            display_group.add(ORANGE_SPRITE_DISPLAY)

            PURPLE_SPRITE_DISPLAY = pygame.sprite.Sprite()
            PURPLE_SPRITE_DISPLAY.image = pygame.transform.scale(PURPLE_SPRITE_IMAGE, (100, 100))
            PURPLE_SPRITE_DISPLAY.rect = PURPLE_SPRITE_DISPLAY.image.get_rect()
            PURPLE_SPRITE_DISPLAY.rect.center = (625, 2 * RES_HEIGHT // 3)
            display_group.add(PURPLE_SPRITE_DISPLAY)

            display_group.draw(self.WINDOW)
            pygame.display.flip()
            done = False
            already_chosen = -1  # placeholder
            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True
                        self.exit_early = True
                        self.running = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if not self.player1_choose:
                            if RED_SPRITE_DISPLAY.rect.collidepoint(mouse_pos) and already_chosen != 1:
                                self.player2_sprite_number = 1
                                display_group.remove(RED_SPRITE_DISPLAY)
                                done = True
                            elif ORANGE_SPRITE_DISPLAY.rect.collidepoint(mouse_pos) and already_chosen != 2:
                                self.player2_sprite_number = 2
                                display_group.remove(ORANGE_SPRITE_DISPLAY)
                                done = True
                            elif GREEN_SPRITE_DISPLAY.rect.collidepoint(mouse_pos) and already_chosen != 3:
                                self.player2_sprite_number = 3
                                display_group.remove(GREEN_SPRITE_DISPLAY)
                                done = True
                            elif PURPLE_SPRITE_DISPLAY.rect.collidepoint(mouse_pos) and already_chosen != 4:
                                self.player2_sprite_number = 4
                                display_group.remove(PURPLE_SPRITE_DISPLAY)
                                done = True

                        if self.player1_choose:
                            if RED_SPRITE_DISPLAY.rect.collidepoint(mouse_pos):
                                self.player1_sprite_number = 1
                                already_chosen = 1
                                self.player1_choose = False
                                RED_SPRITE_DISPLAY.kill()
                            elif ORANGE_SPRITE_DISPLAY.rect.collidepoint(mouse_pos):
                                self.player1_sprite_number = 2
                                already_chosen = 2
                                self.player1_choose = False
                                ORANGE_SPRITE_DISPLAY.kill()
                            elif GREEN_SPRITE_DISPLAY.rect.collidepoint(mouse_pos):
                                self.player1_sprite_number = 3
                                already_chosen = 3
                                self.player1_choose = False
                                GREEN_SPRITE_DISPLAY.kill()
                            elif PURPLE_SPRITE_DISPLAY.rect.collidepoint(mouse_pos):
                                self.player1_sprite_number = 4
                                already_chosen = 4
                                self.player1_choose = False
                                PURPLE_SPRITE_DISPLAY.kill()
                            display_group.update()
                            self.WINDOW.fill(SKY_BLUE)
                            self.WINDOW.blit(p2_select_text, (80, 100))
                            display_group.draw(self.WINDOW)
                            pygame.display.flip()



    def display_end_screen(self):
        if not self.exit_early:
            self.WINDOW.fill(SKY_BLUE)
            myfont = pygame.font.SysFont('helvetica', 40)
            myfont_small = pygame.font.SysFont('helvetica', 30)
            if self.winner == self.player1:
                text = myfont.render('PLAYER 1 WON!', True, BLACK)
                under_text = myfont_small.render('Press space to play again', True, BLACK)
                self.WINDOW.blit(text, (RES_WIDTH/2 - 186, RES_HEIGHT/2 - 20))
                self.WINDOW.blit(under_text, (RES_WIDTH/2 - 186, RES_HEIGHT/2 + 40))
            if self.winner == self.player2:
                text = myfont.render('PLAYER 2 WON!', True, BLACK)
                under_text = myfont_small.render('Press space to play again', True, BLACK)
                self.WINDOW.blit(text, (RES_WIDTH / 2 - 186, RES_HEIGHT / 2 - 20))
                self.WINDOW.blit(under_text, (RES_WIDTH / 2 - 186, RES_HEIGHT / 2 + 40))
            done = False # boolean to keep showing this end screen
            pygame.display.flip()  # screen draw update not reached, manual needed

            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        done = True
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            done = True # move on to next part of running loop: a new game


game_instance = Game()
game_instance.display_start_screen()
game_instance.display_char_selection()
while game_instance.running:
    game_instance.new()
    game_instance.display_end_screen()

pygame.quit()
