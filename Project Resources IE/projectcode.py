import os
import time
import pygame
import sys
import math
import random


layers = {
    "ground_layer" : 1,
    "barrier_layer" : 2,
    "player_layer" : 3,
    "bullet_layer" : 4,
    "enemy_layer" : 3,
    "items_layer" : 2,
    "crosshair_layer" : 5,
}


colours= {
    "black" : [0, 0, 0],
    "white" : [255, 255, 255],
    "red" : [255, 0, 0],
    "orange" : [255, 102, 0],
    "yellow" : [255, 255, 0],
    "green" : [0, 255, 0],
    "blue" : [0, 0, 255],
    "purple" : [128, 0, 128],
    "grey" : [115,115,115],
}

game_title = "Island Escape"
fps = 60
v2 = pygame.math.Vector2
tilesize = 32
screen_width = 1024
screen_height= 768
bullets = []

class Main():
        def __init__(self):
            pygame.init()
            self.screen_width,self.screen_height = 1024, 768
            self.display = pygame.Surface((self.screen_width,self.screen_height))
            self.screen = pygame.display.set_mode((1024, 768))
            self.clock = pygame.time.Clock()
            self.running = True
            self.playing = True
            self.actions = {"left": False, "right": False, "up" : False, "down" : False, "pause" : False, "backspace" : False, "enter" : False, "death" : False}
            self.stack_item = []
            self.load_assets()
            self.load_states()


        def run(self):
            while self.playing:
                self.dt = self.clock.tick(fps)/1000
                self.events()
                self.update()
                self.draw()
            

        def events(self):
            for event in pygame.event.get():
                pygame.event.set_grab(True)
                if event.type == pygame.QUIT:
                    self.playing = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.playing = False
                        self.running = False
                    if event.key == pygame.K_a:
                        self.actions['left'] = True
                    if event.key == pygame.K_d:
                        self.actions['right'] = True
                    if event.key == pygame.K_w:
                        self.actions['up'] = True
                    if event.key == pygame.K_s:
                        self.actions['down'] = True
                    if event.key == pygame.K_p:
                        self.actions['pause'] = True
                    if event.key == pygame.K_BACKSPACE:
                        self.actions['backspace'] = True    
                    if event.key == pygame.K_RETURN:
                        self.actions['enter'] = True 
                        
                        

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.actions['left'] = False
                    if event.key == pygame.K_d:
                        self.actions['right'] = False
                    if event.key == pygame.K_w:
                        self.actions['up'] = False
                    if event.key == pygame.K_s:
                        self.actions['down'] = False
                    if event.key == pygame.K_p:
                        self.actions['pause'] = False
                    if event.key == pygame.K_BACKSPACE:
                        self.actions['backspace'] = False
                    if event.key == pygame.K_RETURN:
                        self.actions['enter'] = False  
                        

                        


        def update(self):
            self.stack_item[-1].update(self.actions)


        def draw(self):
            self.stack_item[-1].draw(self.display)
            # Render current state to the screen
            self.screen.blit(self.display, (0,0))
            self.clock.tick(fps)
            pygame.display.flip()


        def draw_text(self, display, text, color, x, y):
            text_display = self.font.render(text, True, color)
            #text_surface.set_colorkey((0,0,0))
            text_rect = text_display.get_rect()
            text_rect.center = (x, y)
            display.blit(text_display, text_rect)


        def load_assets(self):
            # Create pointers to directories 
            self.assets_dir = os.path.join("assets")
            self.sprite_dir = os.path.join(self.assets_dir, "player")
            self.font_dir = os.path.join(self.assets_dir, "font")
            self.font= pygame.font.Font(os.path.join(self.font_dir, "PressStart2P-Regular.ttf"), 20)


        def load_states(self):
            self.title_screen = MainMenu(self)
            self.stack_item.append(self.title_screen)


        def clear_actions(self):
            for action in self.actions:
                self.actions[action] = False


#------------------------------------------------------------------------------------
class Stack():
    def __init__(self, game):
        self.game = game
        self.initial_state = None


    def update(self, actions):
        pass
    

    def draw(self, display):
        pass


    def update_state(self):
        if len(self.game.stack_item) > 1:
            self.initial_state = self.game.stack_item[-1]
        self.game.stack_item.append(self)


    def change_state(self):
        self.game.stack_item.pop()


#------------------------------------------------------------------------------------
class Game(Stack):
    def __init__(self, game):
        Stack.__init__(self,game)
        self.clock = pygame.time.Clock()
        self.dt = self.clock.tick(fps)/1000
        self.screen_width,self.screen_height = 2048, 1536
        self.assets_dir = os.path.join("assets")
        self.map_img = pygame.image.load(os.path.join(self.assets_dir, "map", "mapped.png"))
        self.player_alive = True
        self.gamewon = False
        self.loadmap()
        self.new()
        

    def update(self, actions):
        # Check if the game was paused 
        if actions["pause"]:
            new_state = PauseMenu(self.game)
            new_state.update_state()
        if not self.player_alive:
            new_state = DeathMenu(self.game)
            new_state.update_state()
        if self.gamewon:
            new_state = Win(self.game)
            new_state.update_state()
        self.all_sprites.update()
        self.camera.update(self.player)
        
    
    
    def loadmap(self):
        self.mapdata = []
        with open(os.path.join(self.assets_dir, 'map', 'map.txt'), 'rt') as file:
            for row in file:
                self.mapdata.append(row)

    
    def draw_sprites(self):
        for row, tiles in enumerate(self.mapdata):
            for column, tiles1 in enumerate(tiles):
                if tiles1 == '1':
                    MapBarriers(self, column, row)
                if tiles1 == 'E':
                    self.enemy = Enemy(self, column, row)
                if tiles1 == 'B' and len(self.enemies) == 0:
                    pass                    
                if tiles1 == 'P':
                    self.player = Player(self, column, row)
                    
        
        
    def new(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.crosshair_group = pygame.sprite.Group()
        self.barriers = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.map = Map(self, 0, 0)
        self.crosshair = Crosshair(self)
        self.camera = Camera(self.screen_width, self.screen_height)
        self.draw_sprites()
        
        
    

    def draw(self, display):
        display.fill(colours["grey"])
        for sprite in self.all_sprites:
            display.blit(sprite.image, self.camera.camera_move(sprite))
        for bullet in self.bullets:
            bullet.update()
        pygame.display.flip()
      

#------------------------------------------------------------------------------------ 
class MainMenu(Stack):
    def __init__(self, game):
        Stack.__init__(self, game)
        self.mmenu_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "mainmenu.png"))
        self.mmenu_rect = self.mmenu_img.get_rect() 
        self.mmenu_options = {0: "Start", 1: "ControlMenu", 2: "Exit"}
        self.index = 0
        self.cursor_img = pygame.image.load(os.path.join(self.game.assets_dir, "extra", "cursor.png"))
        self.cursor_rect = self.cursor_img.get_rect()
        self.cursor_posy = self.mmenu_rect.y + 435
        self.cursor_posx = self.mmenu_rect.x + 335
        self.cursor_rect.y = self.cursor_posy
        self.cursor_rect.x = self.cursor_posx
  

    def update(self, actions):
        self.update_cursor(actions)      
        if actions["enter"]:
            self.transition_state()
        self.game.clear_actions()
    
        
    def draw(self, display):
        display.blit(self.mmenu_img, self.mmenu_rect)
        display.blit(self.cursor_img, self.cursor_rect)
    
    
    def transition_state(self):
        if self.mmenu_options[self.index] == "Start": 
            new_state = Game(self.game)
            new_state.update_state()
        elif self.mmenu_options[self.index] == "ControlMenu": 
            new_state = ControlMenu(self.game)
            new_state.update_state()
        elif self.mmenu_options[self.index] == "Exit":
            self.game.playing = False
            self.game.running = False
            
    
    def update_cursor(self, actions):
        if actions['down']:
            self.index = (self.index + 1) % len(self.mmenu_options)
        elif actions['up']:
            self.index = (self.index - 1) % len(self.mmenu_options)
        self.cursor_rect.y = self.cursor_posy + (self.index * 70)


#------------------------------------------------------------------------------------
class PauseMenu(Stack):
    def __init__(self, game):
        self.game = game
        Stack.__init__(self, game)
        # Set the menu
        self.pmenu_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "pamenu.png"))
        self.pmenu_rect = self.pmenu_img.get_rect()
        # Set the cursor and menu states
        self.pmenu_options = {0 :"ControlMenu", 1 : "Exit"}
        self.index = 0
        self.cursor_img = pygame.image.load(os.path.join(self.game.assets_dir, "extra", "selectbox.png"))
        self.cursor_rect = self.cursor_img.get_rect()
        self.cursor_posy = self.pmenu_rect.y + 527
        self.cursor_posx = self.pmenu_rect.x + 331    
        self.cursor_rect.y = self.cursor_posy
        self.cursor_rect.x = self.cursor_posx
  

    def update(self, actions):  
        self.update_cursor(actions)      
        if actions["enter"]:
            self.transition_state()
        if actions["backspace"]:
            self.change_state()
        self.game.clear_actions()


    def draw(self, display):
        # render the gameworld behind the menu, which is right before the pause menu on the stack
        #self.game.stack_item[-2].render(display)
        self.initial_state.draw(display)
        display.blit(self.pmenu_img, self.pmenu_rect)
        display.blit(self.cursor_img, self.cursor_rect)


    def transition_state(self):
        if self.pmenu_options[self.index] == "ControlMenu": 
            new_state = ControlMenu(self.game)
            new_state.update_state()
        elif self.pmenu_options[self.index] == "Exit": 
            while len(self.game.stack_item) > 1:
                self.game.stack_item.pop()


    def update_cursor(self, actions):
        if actions['left']:
            self.index = (self.index - 1) % len(self.pmenu_options)
        elif actions['right']:
            self.index = (self.index + 1) % len(self.pmenu_options)
        self.cursor_rect.x = self.cursor_posx + (self.index * 225)


#------------------------------------------------------------------------------------
class ControlMenu(Stack):
    def __init__(self, game):
        self.game = game
        Stack.__init__(self, game)
        self.smenu_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "smenu.png"))
        self.smenu_rect = self.smenu_img.get_rect()
        # Set the cursor and menu states
        self.smenu_options = {0 :"Exit"}
        self.index = 0
        self.cursor_img = pygame.image.load(os.path.join(self.game.assets_dir, "extra", "selectbox.png"))
        self.cursor_rect = self.cursor_img.get_rect()
        self.cursor_posy = self.smenu_rect.y + 630
        self.cursor_posx = self.smenu_rect.x + 900   
        self.cursor_rect.y = self.cursor_posy
        self.cursor_rect.x = self.cursor_posx
  

    def update(self, actions):       
        if actions["enter"]:
            self.change_state()
        self.game.clear_actions()


    def draw(self, display):
        # render the gameworld behind the menu, which is right before the pause menu on the stack
        #self.game.stack_item[-2].render(display)
        display.blit(self.smenu_img, self.smenu_rect)
        display.blit(self.cursor_img, self.cursor_rect)


    def transition_state(self):
        if self.smenu_options[self.index] == "Exit": 
            new_state = MainMenu(self.game)
            new_state.update_state()

        
#-----------------------------------------------------------------------------------
class DeathMenu(Stack):
    def __init__(self, game):
        self.game = game
        Stack.__init__(self, game)
        # Set the menu
        self.dmenu_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "death.png"))
        self.dmenu_rect = self.dmenu_img.get_rect()
        # Set the cursor and menu states
        self.dmenu_options = {0 :"Controls", 1 : "Restart", 2 : "Exit"}
        self.index = 0
        self.cursor_img = pygame.image.load(os.path.join(self.game.assets_dir, "extra", "selectbox.png"))
        self.cursor_rect = self.cursor_img.get_rect()
        self.cursor_posy = self.dmenu_rect.y + 433
        self.cursor_posx = self.dmenu_rect.x + 238
        self.cursor_rect.y = self.cursor_posy
        self.cursor_rect.x = self.cursor_posx
  

    def update(self, actions):  
        self.update_cursor(actions)      
        if actions["enter"]:
            self.transition_state()
        self.game.clear_actions()
            


    def draw(self, display):
        display.blit(self.dmenu_img, self.dmenu_rect)
        display.blit(self.cursor_img, self.cursor_rect)


    def transition_state(self):
        if self.dmenu_options[self.index] == "Controls": 
            new_state = ControlMenu(self.game)
            new_state.update_state()
        if self.dmenu_options[self.index] == "Restart":
            while len(self.game.stack_item) > 1:
                self.game.stack_item.pop() 
            new_state = Game(self.game)
            new_state.update_state()
            time.sleep(3)
        if self.dmenu_options[self.index] == "Exit": 
            while len(self.game.stack_item) > 1:
                self.game.stack_item.pop()


    def update_cursor(self, actions):
        if actions['left']:
            self.index = (self.index - 1) % len(self.dmenu_options)
        elif actions['right']:
            self.index = (self.index + 1) % len(self.dmenu_options)
        self.cursor_rect.x = self.cursor_posx + (self.index * 230)
        
        
#-----------------------------------------------------------------------------------       
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = layers["player_layer"]
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image_original = pygame.image.load(os.path.join(self.game.assets_dir, "player", "Survivor32.png")).convert_alpha()
        self.image = self.image_original.copy()
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.x = x * tilesize
        self.rect.y = y * tilesize
        self.pos = v2(self.x, self.y) * tilesize
        self.vel = 15
        self.velx = 0
        self.vely = 0
        self.rot = 0
        self.rotate_vel = v2(0, 0)
        self.mposx, self.mposy = pygame.mouse.get_pos()
        self.vec_x, self.vec_y = pygame.mouse.get_pos() - self.pos
        self.angle = -math.degrees(math.atan2(self.vec_y, self.vec_x))
        self.firerate_delay = 300
        self.check_shot = 0
        
        

        
    
    
    def update(self):
        self.movement()
        self.x += self.velx * self.game.dt
        self.rect.x = self.x
        self.y += self.vely * self.game.dt
        self.rect.y = self.y
        self.pos = v2(self.x, self.y) * tilesize
        self.rotate()
        self.enemy_collide()
        
    
 
    def rotate(self):
        self.vec_x, self.vec_y = pygame.mouse.get_pos() - self.pos
        self.angle = -math.degrees(math.atan2(self.vec_y, self.vec_x))
        self.image = pygame.transform.rotate(self.image_original, int(self.angle))
        self.rect = self.image.get_rect()
        self.rect.center = v2(self.x, self.y) * tilesize
    
    def enemy_collide(self):
        hit_detect = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hit_detect:
            self.kill()
            self.game.player_alive = False

        
    
    def movement(self):
        self.velx = 0
        self.vely = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_a] or key[pygame.K_LEFT]:
            self.velx = -self.vel
        if key[pygame.K_d] or key[pygame.K_RIGHT]:
            self.velx = self.vel
        if key[pygame.K_w] or key[pygame.K_UP]:
            self.vely = -self.vel
        if key[pygame.K_s] or key[pygame.K_DOWN]:
            self.vely = self.vel
        if self.velx != 0 and self.vely != 0:
            self.velx *= 0.7071
            self.vely *= 0.7071
        if key[pygame.K_SPACE]:
            cooldown = pygame.time.get_ticks()
            if cooldown - self.check_shot > self.firerate_delay:
                self.check_shot = cooldown
                Bullet(self.game, self.game.player.rect.x, self.game.player.rect.y)
    

    def barrier_collide(self, dir):
        if dir == "x":
            hit = pygame.sprite.spritecollide(self, self.game.barriers, False)
            if hit:
                if self.velx > 0:
                    self.rect.x = hit[0].rect.left - self.rect.width
                if self.velx < 0:
                    self.rect.x = hit[0].rect.right
        if dir == "x":
            hit = pygame.sprite.spritecollide(self, self.game.barriers, False)
            if hit:
                if self.vely > 0:
                    self.rect.x = hit[0].rect.top - self.rect.height
                if self.vely < 0:
                    self.rect.x = hit[0].rect.bottom
    
        
        
    
    def draw(self, display):
       display.blit(self.image, (self.x, self.y))
        
        
#------------------------------------------------------------------------------------   
class Map(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = layers["ground_layer"]
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.image.load(os.path.join(self.game.assets_dir, "map", "mapped.png"))
        self.rect = self.image.get_rect()
        self.x = x * tilesize
        self.y = y * tilesize
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, display):
        display.blit(self.image, (self.x, self.y))
        
        
#------------------------------------------------------------------------------------      
class MapBarriers(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = layers["barrier_layer"]
        self.groups = game.all_sprites, game.barriers
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface ((tilesize, tilesize))
        self.image.fill(colours["grey"])
        self.rect = self.image.get_rect()
        self.x = x * tilesize
        self.y = y * tilesize
        self.rect.x = self.x
        self.rect.y = self.y
        self.width = tilesize
        self.height = tilesize
    
    
    def draw(self, display):
        display.blit(self.image, (self.x, self.y))
   
    
#------------------------------------------------------------------------------------
class Crosshair(pygame.sprite.Sprite):
    def __init__(self, game):
        self._layer = layers["crosshair_layer"]
        self.groups = game.all_sprites, game.crosshair_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.image.load(os.path.join(self.game.assets_dir, "extra", "crosshair.png"))
        self.rect = self.image.get_rect()
        
    
    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        
        
    def draw(self, display):
        display.blit(self.image, self)
        
        
 #------------------------------------------------------------------------------------       
class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = layers["enemy_layer"]
        self.groups = game.all_sprites, game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.mob_img = pygame.image.load(os.path.join(self.game.assets_dir, "player", "BearSize1.png")).convert_alpha()
        self.image = self.mob_img.copy()
        self.x = x * tilesize
        self.y = y * tilesize
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.pos = v2(x, y) * tilesize
        self.rect.center = self.pos
        self.vel = v2(0, 0)
        self.acc = v2(0, 0)
        self.speed = random.randint(1000, 2000)
        self.friction = -5
        self.fan_out = 50
         
    
    def update(self):
        rel_x, rel_y = self.game.player.pos - self.pos
        angle = -math.degrees(math.atan2(rel_y, rel_x))
        self.image = pygame.transform.rotate(self.mob_img, int(angle))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.acc = v2(self.speed, 0).rotate(-int(angle))
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * self.friction
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
        self.rect.center = self.pos
        if pygame.sprite.spritecollideany(self, self.game.bullets):
            self.kill()
            if not self.game.enemies:
                self.game.gamewon = True
     

    

    def draw(self, display):
        display.blit(self.image, (self.x, self.y))
        


 #------------------------------------------------------------------------------------  
class Camera():
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def camera_move(self, sprite):
        return sprite.rect.move(self.camera.topleft)
    
    def update(self, main):
        x = -main.rect.x + int(screen_width/2)
        y = -main.rect.y + int(screen_height/2)
        self.camera = pygame.Rect(x, y, self.width, self.height)
 #------------------------------------------------------------------------------------  
class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.bullets
        self._layer = layers["player_layer"]
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.bullet_img = pygame.image.load(os.path.join(self.game.assets_dir, "extra", "bullet.png"))
        self.image = self.bullet_img.copy()
        self.rect = self.image.get_rect()
        self.pos = v2(x, y)
        self.rect.center = x, y
        self.mx, self.my = pygame.mouse.get_pos()
        self.speed = 15
        self.vec_x, self.vec_y = pygame.mouse.get_pos() - self.pos
        self.angle = math.atan2(self.vec_y, self.vec_x)    
        self.velx = math.cos(self.angle) * self.speed
        self.vely = math.sin(self.angle) * self.speed
        self.release = pygame.time.get_ticks()
        self.dropoff = 250
    
    def update(self):
        self.rect.x += int(self.velx)
        self.rect.y += int(self.vely)
        if pygame.sprite.spritecollideany(self, self.game.barriers):
            self.kill()
        if pygame.time.get_ticks() - self.release > self.dropoff:
            self.kill()
#------------------------------------------------------------------------------------  
class Win(Stack):
    def __init__(self, game):
        self.game = game
        Stack.__init__(self, game)
        # Set the menu
        self.wmenu_img = pygame.image.load(os.path.join(self.game.assets_dir, "map", "winner.png"))
        self.wmenu_rect = self.wmenu_img.get_rect()
        # Set the cursor and menu states
        self.wmenu_options = {0 :"Controls", 1 : "Restart", 2 : "Exit"}
        self.index = 0
        self.cursor_img = pygame.image.load(os.path.join(self.game.assets_dir, "extra", "selectbox.png"))
        self.cursor_rect = self.cursor_img.get_rect()
        self.cursor_posy = self.wmenu_rect.y + 433
        self.cursor_posx = self.wmenu_rect.x + 238
        self.cursor_rect.y = self.cursor_posy
        self.cursor_rect.x = self.cursor_posx
  

    def update(self, actions):  
        self.update_cursor(actions)      
        if actions["enter"]:
            self.transition_state()
        self.game.clear_actions()
            


    def draw(self, display):
        display.blit(self.wmenu_img, self.wmenu_rect)
        display.blit(self.cursor_img, self.cursor_rect)


    def transition_state(self):
        if self.wmenu_options[self.index] == "Controls": 
            new_state = ControlMenu(self.game)
            new_state.update_state()
        if self.wmenu_options[self.index] == "Restart":
            while len(self.game.stack_item) > 1:
                self.game.stack_item.pop() 
            new_state = Game(self.game)
            new_state.update_state()
            time.sleep(3)
        if self.wmenu_options[self.index] == "Exit": 
            while len(self.game.stack_item) > 1:
                self.game.stack_item.pop()

    

     
if __name__ == "__main__":
    g = Main()
    while g.running:
        pygame.mouse.set_visible(False)
        g.run()