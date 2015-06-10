from __future__ import division
import pygame
import sys
import os
import random
import math

def load_image(filename):
	"""Load an image with the given filename from the images directory"""
	return pygame.image.load(os.path.join('images', filename))
	
def load_music(filename):
	"""Load a sound with the given filename from the images directory"""
	return pygame.mixer.Sound(os.path.join('sound', filename))
	
def draw_centered(sur1, sur2, pos):
	"""Draw an image centered at given position"""
	rect = sur1.get_rect()
	rect = rect.move(pos[0] - rect.width//2, \
					 pos[1] - rect.height//2)
	sur2.blit(sur1, rect)
	
def distance(p, q):
    """Return the distance between points p and q"""
    return math.sqrt((p[0]-q[0])**2 + (p[1]-q[1])**2)
    
class GameObject(object):
	"""Base class for every object in this game"""
	def __init__(self, pos, image):
	 	"""Initialize object's position and image"""
	 	self.pos = pos
	 	self.image = image
	 	
	def draw_on(self, screen):
	 	"""Draw image centered at given position"""
	 	return draw_centered(self.image, screen, self.pos)
	 	
class Ghost(GameObject):
	"""Initial Ghost's speed"""
	SPEED = 10
	def __init__(self, pos):
		"""Ghost object, creates the main character of the game."""
		super(Ghost, self).__init__(pos, load_image('ghost.png'))
		self.speed = Ghost.SPEED
		self.dir = (0, 0)
		
	def move(self):
		"""Move Ghost using directory and speed"""
		rect = self.image.get_rect()
		self.pos = (self.pos[0]+self.dir[0]*self.speed,\
						 self.pos[1]+self.dir[1]*self.speed)
		rect = rect.move(self.pos)
		
class Enemy(GameObject):
	"""Initial Enemies's speed"""
	SPEED = 2
	def __init__(self, pos):
		"""Creates monsters, Ghost's enemies"""
		super(Enemy, self).__init__(pos, load_image('enemy.png'))
		self.speed = Enemy.SPEED
	def move(self, ghost_pos):
		"""Moves Monsters to the ghost's place"""
		v = (ghost_pos[0] - self.pos[0], ghost_pos[1] - self.pos[1])
		dis = distance(ghost_pos, self.pos)
		if dis != 0:
			uv = v[0]/dis, v[1]/dis
			self.pos = (self.pos[0] + uv[0]*self.speed, \
						self.pos[1] + uv[1]*self.speed)
						
class Shoot(GameObject):
	"""Creates Ghost's shoots which kills Monsters"""
	def __init__(self, pos):
		super(Shoot, self).__init__(pos, load_image('power_ball.png'))
		self.speed = 8
	def shoot(self, pos):
		"""Moves shoots to the mouse_position"""
		v = (pos[0] - self.pos[0], pos[1] - self.pos[1])
		dis = distance(pos, self.pos)
		if dis != 0:
			uv = v[0]/dis, v[1]/dis
			self.pos = (self.pos[0] + uv[0]*self.speed, \
						self.pos[1] + uv[1]*self.speed)
						
class Lives(GameObject):
	"""Creates Lives objects"""
	def __init__(self, pos):
		super(Lives, self).__init__(pos, load_image('heart.png'))
		
class Crystals(GameObject):
	IMAGES =  [load_image('crystal1.png'),
		       load_image('crystal2.png'),
			   load_image('crystal3.png')]
	
	def __init__(self, pos):
		"""Creates crystals with random picture"""
		super(Crystals, self).__init__(pos, random.choice(Crystals.IMAGES))
		
class Game(object):
	"""Main Class"""
	"""Game states"""
	PLAYING, GAME_OVER, INTERFACE, NEW_LVL, WIN = range(5)
	"""Additional Game events"""
	REFRESH, START, RESTART = range(pygame.USEREVENT, pygame.USEREVENT+3)
	
	"""Default list for Ghost's lives"""
	LIVES = [Lives((150, 30)), Lives((200, 30)), Lives((250, 30))]
	
	"""Default number of crystals and monsters"""
	CRYSTAL_NUM = 2
	ENEMIES_NUM = 1
	def __init__(self):
		pygame.init()
		pygame.mixer.init()
		
		"""Screen Settings"""
		self.width = 800
		self.height = 600
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.display.set_caption('Ghost vs Monster!')
		
		"""Background color(black)"""
		self.bg_color = 0, 0, 0
		
		"""Text settings(color, size, font)"""
		self.txt_color = (255,	131, 250)
		self.txt1 = pygame.font.Font('Minecraftia.ttf', 30)
		self.txt2 = pygame.font.Font('Minecraftia.ttf', 100)
		
		"""Background pictures of web for every screen's angle"""
		self.web1 = load_image('web1.png')
		self.web2 = load_image('web2.png')
		self.web3 = load_image('web3.png')
		self.web4 = load_image('web4.png')
		
		"""Main character"""
		self.ghost = Ghost((self.width//2, self.height//2))
		
		"""Variable for lives, level and score"""
		self.lives = Game.LIVES[:]
		self.level = 1
		self.score = 0
		
		"""Load music and sound effect's for game"""
		self.gameover_sound = load_music('death.wav')
		self.new_lvlsound = load_music('new_lvl.wav')
		self.soundtrack = load_music('soundtrack.wav')
		self.shoot_sound = load_music('shoot.wav')
		self.win_sound = load_music('win.wav')
		
		"""Set variables for shoot's, crystal's and enemies' objects,
		   plus for game state and mouse position"""
		self.shoot   = []
		self.crystal = []
		self.enemy   = []
		self.state   = Game.INTERFACE
		self.mouse_pos = None
		
		"""Setup timer to refresh display fps times per second"""
		self.FPS = 30
		pygame.time.set_timer(Game.REFRESH, 1000//self.FPS)
		
		
	def run(self):
		"""Loop forever processing events"""
		running = True
		while running:
			event = pygame.event.wait()
			if event.type == pygame.QUIT or \
			   event.type == pygame.KEYDOWN and \
			   event.key  == pygame.K_ESCAPE:
			   """Stops program if user wants to quit"""
			   running = False
			
			elif self.state == Game.INTERFACE and \
				 event.type == pygame.KEYDOWN and \
				 event.key  == pygame.K_RETURN:
				 """Restarts game when Return key was pressed"""
				 self.restart()
				
			elif event.type == Game.RESTART:
				"""Restarts game"""
				pygame.time.set_timer(Game.RESTART, 0)
				if len(self.lives) > 0 and \
				   self.state != Game.WIN:
					self.state = Game.PLAYING
					self.start()
				elif self.state == Game.GAME_OVER or \
					 self.state == Game.WIN:
					self.state = Game.INTERFACE
					
			elif event.type == pygame.MOUSEBUTTONDOWN and \
				 self.state == Game.PLAYING:
				"""Gets mouse position and creates new Shoot object"""
				self.mouse_pos = pygame.mouse.get_pos()
				self.shoot.append(Shoot(self.ghost.pos))
				self.shoot_sound.play()
						
			elif event.type == pygame.KEYDOWN and \
				 self.state == Game.PLAYING:
				"""Changes direction of Ghost object"""
				if event.key == pygame.K_s:
					self.ghost.dir = (0, 1)
				elif event.key == pygame.K_a:
					self.ghost.dir = (-1, 0)
				elif event.key == pygame.K_w:
					self.ghost.dir = (0, -1) 
				elif event.key == pygame.K_d:
					self.ghost.dir = (1, 0)
				
			elif event.type == pygame.KEYUP and \
				 self.state == Game.PLAYING:
				"""Stops ghost if none of the required key was pressed"""
				self.ghost.dir = (0, 0)
				
			elif event.type == Game.REFRESH:
				"""Refreshes the display"""
				self.draw()
				pygame.display.flip()
				
	def restart(self):
		"""Restart method, sets lives, score and level variables to default values"""
		self.lives = Game.LIVES[:]
		self.score = 0
		self.level = 1
		self.start()
		
	def start(self):
		"""Start method, plays soundtrack, sets ghost settings and creates crystals and
		   enemies, number depends from level"""
		self.soundtrack.play(-1, 0, 1000)
		self.soundtrack.set_volume(0.5)
		self.ghost.dir = (0, 0)
		self.ghost.pos = [self.width//2, self.height//2]
		self.crystal = {self.new_crystals() for _ in range(Game.CRYSTAL_NUM+self.level)}
		self.enemy = {self.new_enemy() for _ in range(Game.ENEMIES_NUM*self.level)}
		for i in self.enemy:
			i.speed += self.level
		self.state = Game.PLAYING	
	
	def new_lvl(self):
		"""New level method, gives some time between levels"""
		self.soundtrack.stop()
		self.state = Game.NEW_LVL
		self.new_lvlsound.play()
		delay = int((self.new_lvlsound.get_length()+1)*1000)
		pygame.time.set_timer(Game.RESTART, delay)
		
	def game_over(self):
		"""Game over method, gives some time between the death and
		   interface modes"""
		self.soundtrack.stop()
		self.state = Game.GAME_OVER
		self.gameover_sound.play()
		delay = int((self.gameover_sound.get_length()+1)*1000)
		pygame.time.set_timer(Game.RESTART, delay)
	
	def win(self):
		"""Win method, gives some time between win and interface modes"""
		self.soundtrack.stop()
		self.state = Game.WIN
		self.win_sound.play()
		delay = int((self.win_sound.get_length()+1)*1000)
		pygame.time.set_timer(Game.RESTART, delay)
			
	def new_crystals(self):
		"""Creates new crystals"""
		return Crystals(self.good_position())
		
	def new_enemy(self):
		"""Creates new monsters"""
		return Enemy(self.good_position())
	
	def interface(self):
		"""Interface mode, prints picture with instructions"""
		image = load_image('interface.png')
		draw_centered(image, self.screen, (self.width//2, self.height//2))
		
	
	def draw(self):
		"""Draw method, prints current situation"""
		"""Game background"""
		self.screen.fill(self.bg_color)
		draw_centered(self.web1, self.screen, (100,110))
		draw_centered(self.web2, self.screen, (100, 490))
		draw_centered(self.web3, self.screen, (700, 490))
		draw_centered(self.web4, self.screen, (700, 100))
		
		if self.state  == Game.INTERFACE:
			"""Prints interface"""
			self.interface()
			
		elif self.state == Game.NEW_LVL:
			"""Prints level message"""
			lvl_txt = self.txt2.render(("Level %d!" % self.level), True, self.txt_color)
			draw_centered(lvl_txt, self.screen, (self.width//2, self.height//2))
		
		elif self.state == Game.GAME_OVER:
			"""Prints game over method"""
			game_over = self.txt2.render("Game Over!", True, self.txt_color)
			draw_centered(game_over, self.screen, (self.width//2, self.height//2))
		
		elif self.state == Game.WIN:
			"""Prints win message and your final score"""
			win = self.txt1.render(("You are Winner!"),True, self.txt_color)
			draw_centered(win, self.screen, (self.width//2, self.height//2))
			score = self.txt1.render(("Your final score is %d!" % self.score), True, self.txt_color)
			draw_centered(score, self.screen, (self.width//2, self.height-250))
			
		elif self.state == Game.PLAYING:
			"""Prints you life and score, plus checks if you've touched any of given 
			   objects"""
			lives_txt = self.txt1.render("Lives:", True, self.txt_color)
			draw_centered(lives_txt, self.screen, (70, 30))
		
			score_txt = self.txt1.render(("Score: %d" % self.score), True, self.txt_color)
			draw_centered(score_txt, self.screen, (650, 30))
			
			self.ghost.move()
			self.ghost.draw_on(self.screen)	
			self.draw_hearts()
			
			if len(self.shoot) != 0:
				self.draw_shoot(self.mouse_pos)
				self.shoot_enemy()
			
			"""Draws crystals and monsters on the screen, plus
			   checkes if ghost touched one of them or not.
			   Must be in try/except in case of error"""	
			try:
				for i in self.crystal:
					i.draw_on(self.screen)
					self.touched_crystal(i)
			except: pass
			
			try:
				for j in self.enemy:
					j.move(self.ghost.pos)
					j.draw_on(self.screen)
					self.touched_enemy(j)
			except: pass
			
	def draw_hearts(self):
		"""Draws Ghost's lives"""
		for i in self.lives:
			i.draw_on(self.screen)
			
	def draw_shoot(self, pos):
		"""Moves and draws ghost's shoots"""
		self.shoot[-1].shoot(pos)
		self.shoot[-1].draw_on(self.screen)
		
	def shoot_enemy(self):
		"""Checks if enemies was shouted by Ghost"""
		if distance(self.shoot[-1].pos, self.mouse_pos) < 1:
				del self.shoot[-1]
		try:
			for i in self.enemy:
				if len(self.shoot) != 0 and \
					distance(self.shoot[-1].pos, i.pos) < 60:
					del self.shoot[-1]
					pos = i.pos
					self.enemy.remove(i)
					draw_centered(load_image('dust.png'), self.screen, pos)
		except:pass
	
	def touched_crystal(self, i):
		"""Checks if ghost touched crystal"""
		if distance(self.ghost.pos, i.pos) < 80:
			self.crystal.remove(i)
			self.score += 1000
		if len(self.crystal) == 0:
			self.level += 1
			if self.level < 8:
				self.state = Game.NEW_LVL
				self.new_lvl()
			else:
				self.win()
				
	def touched_enemy(self, i):
		"""Checks if ghost touched monster"""
		if distance(self.ghost.pos, i.pos) < 80 and len(self.lives) > 0:
			del self.lives[-1]
			self.enemy.remove(i)
		if len(self.lives) == 0:
				self.game_over()
				
	def good_position(self):
		"""Creates a good position"""
		good = False
		while not good:
			pos = random.randint(50, self.width-50), \
				  random.randint(50, self.height-50)
			good = True
			if distance(self.ghost.pos, pos) < 200:
				good = False
			for x in list(self.enemy) + list(self.crystal):
				if distance(x.pos, pos) < 50:
					good = False
		return pos
		
Game().run()
pygame.quit()
sys.exit()