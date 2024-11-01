'''

Prerequisites:
	Python
	Pygame
	OOP

'''

import pygame
import random
import time
from enum import Enum

print("Space to Shoot and Arrows to Move and Jump")
print("Game Starts...")

class Color(Enum):
	BLACK = (0, 0, 0)
	WHITE = (255, 255, 255)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	DARKGREEN = (0, 128, 0)

WINX = 500
WINY = 480
pil = pygame.image.load

class Character(object):
	def __init__(self, posx, posy, width, height, velocity):
		self.posx = posx
		self.posy = posy
		self.width = width
		self.height = height
		self.velocity = velocity
		self.walkCount = 0

class Player(Character):
	walkLeft = [pil(f'Assets/L{i}.png') for i in range(1, 10)]
	walkRight = [pil(f'Assets/R{i}.png') for i in range(1, 10)]
	standStill = pil('Assets/standing.png')

	def __init__(self, posx, posy, width, height, velocity):
		super().__init__(posx, posy, width, height, velocity)
		self.isJump = False
		self.left = False
		self.right = False
		self.standing = True
		self.hitbox = (self.posx + 20, self.posy + 12, 25, 50)

	def draw(self, win):
		coordinate_player = (self.posx, self.posy)
		if self.walkCount  + 1 >= 27:
			self.walkCount = 0
		if not self.standing:
			if self.left:
				win.blit(self.walkLeft[self.walkCount//3], coordinate_player)
				self.walkCount += 1
			elif self.right:
				win.blit(self.walkRight[self.walkCount//3], coordinate_player)
				self.walkCount += 1
		else:
			if self.left:
				win.blit(self.walkLeft[0], coordinate_player)
			elif self.right:
				win.blit(self.walkRight[0], coordinate_player)
			else:
				win.blit(self.standStill, coordinate_player)
				walkCount = 0

		self.hitbox = (self.posx + 20, self.posy + 12, 25, 50)
		pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

	def hit(self):		# when player gets hit
		print("GROUND 1: ", self.posy)
		messages_list = ["Ooooops", "Good Try", "Well Played", "Try Again", "Yummy", "Not Today", "Go Away", "Hard Luck", "One Last Time", "Interesting?"]
		self.isJump = False
		jump_velocity = jump_height
		if self.posx != 10 and self.posy != 400:
			self.posx = 10
			self.posy = 400
		else:
			self.posx = 150
			self.posy = 400
		self.walkCount = 0
		font = pygame.font.SysFont('comicsans', 64, True)
		text = font.render(random.choice(messages_list), 1, Color.RED.value)
		win.blit(text, (WINX//2 - (text.get_width()//2), WINY//2))
		pygame.display.update()
		print("Goblin caught you, wait 5s")
		try:
			i = 0
			while i < 300:
				pygame.time.delay(10)
				i += 1
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						i = 501
						pygame.quit()
		except Exception as e:
			print("Error: ", e)
		finally:
			print("Move now!")
		print("GROUND 2: ", self.posy)

class Enemy(Character):
	walkLeft = [pil(f'Assets/L{i}E.png') for i in range(1, 12)]
	walkRight = [pil(f'Assets/R{i}E.png') for i in range(1, 12)]

	def __init__(self, posx, posy, width, height, end, velocity, health, damage):
		super().__init__(posx, posy, width, height, velocity)
		self.end = end
		self.health = health
		self.damage = damage
		self.path = [self.posx - self.end, self.posx, self.posx + self.end]
		self.hitbox = (self.posx + 17, self.posy + 2, 40, 55)
		self.visible = True
		self.maxhealth = self.health

	def draw(self, win, player1):
		self.move(player1)
		coordinate_enemy = (self.posx, self.posy)
		if self.visible:
			if self.walkCount + 1 >= 33:
				self.walkCount = 0
			if self.velocity > 0:
				win.blit(self.walkRight[self.walkCount//3], coordinate_enemy)
				self.walkCount += 1
			else:
				win.blit(self.walkLeft[self.walkCount//3], coordinate_enemy)
				self.walkCount += 1
			pygame.draw.rect(win, Color.RED.value, (self.hitbox[0], self.hitbox[1] - 20, 50, 10))
			pygame.draw.rect(win, Color.DARKGREEN.value, (self.hitbox[0], self.hitbox[1] - 20, 50 - (50 * ((self.maxhealth - self.health)/self.maxhealth)), 10))
			self.hitbox = (self.posx + 17, self.posy + 2, 40, 55)
		pygame.draw.rect(win, (255, 0, 0), self.hitbox, 2)

	def move(self, player1):
		if self.velocity > 0:	# move right
			if self.posx + self.velocity < self.path[2]:
				self.posx += self.velocity
			else:	# turn left
				self.velocity = self.velocity * -1
				self.walkCount = 0
		else:	# move left
			if self.posx - self.velocity > self.path[0]:
				self.posx += self.velocity
			else:	# turn right
				self.velocity = self.velocity * -1
				self.WalkCount = 0

	def hit(self, damage):		# when goblin gets hit
		if self.health - damage > 0:
			self.health -= damage
		else:
			self.visible = False
		print("Hit!")

class Projectile(object):
	def __init__(self, posx, posy, radius, facing, color, velocitymultiplier, damage):
		self.posx = posx
		self.posy = posy
		self.radius = radius
		self.facing = facing
		self.color = color
		self.velocitymultiplier = velocitymultiplier
		self.damage = damage

		self.velocity = velocitymultiplier * facing

	def draw(self, win):
		coordinate_projectile = (self.posx, self.posy)
		pygame.draw.circle(win, self.color, coordinate_projectile, self.radius)

def redrawGameWindow():
	coordinate_bg = (0, 0)
	coordinate_score = (250, 10)
	bg = pil('Assets/bg.jpg')
	text = font.render(f'Score: {score}/200', 1, Color.BLACK.value)
	win.blit(bg, coordinate_bg)
	player1.draw(win)
	goblin.draw(win, player1)
	win.blit(text, coordinate_score)
	for i in range(len(bullets)):
		bullets[i].draw(win)
	pygame.display.update()

if __name__ == '__main__':
	pygame.init()

	win = pygame.display.set_mode((WINX, WINY))

	font = pygame.font.SysFont('comicsans', 16, True)
	win.fill(Color.BLACK.value)
	text = font.render(f"Welcome to Goblin Hunter 1.0", 1, Color.GREEN.value)
	win.blit(text, (WINX//2 - (text.get_width()//2), WINY//2))
	pygame.display.update()
	pygame.time.delay(3000)

	pygame.display.set_caption(("Goblin Hunter"))
	bulletSound = pygame.mixer.Sound('Assets/bullet.mp3')
	hitSound = pygame.mixer.Sound('Assets/hit.mp3')
	pygame.mixer.music.load('Assets/bgm.mp3')
	pygame.mixer.music.play(-1)		# -1 for looping song

	clock = pygame.time.Clock()
	random.seed(time.time())

	font = pygame.font.SysFont('comicsans', 32, True)	# font-name, font-size, isBold?
	player1 = Player(
		posx = 50,
		posy = 400,
		width = 64,
		height = 64,
		velocity = 10
	)

	goblin = None

	bullets = []
	jump_gravity = 5
	jump_height = 30
	jump_velocity = jump_height
	total_bullets = 6
	fireratecontroller = 0
	score = 0

	starttime = time.time()
	run = True
	while run and -200 < score < 200:
		clock.tick(27)

		if goblin and goblin.visible == True:
			# is Top of Player inside Bottom Line of Goblin's Hitbox
			isPlayerTopInside = player1.hitbox[1] < goblin.hitbox[1] + goblin.hitbox[3]
			# is Bottom of Player inside Top Line of Goblin's Hitbox
			isPlayerBottomInside = player1.hitbox[1] + player1.hitbox[3] > goblin.hitbox[1]
			# is Left of Player inside Right Line of Goblin's Hitbox
			isPlayerLeftInside = player1.hitbox[0] < goblin.hitbox[0] + goblin.hitbox[2]
			# is Right of Player inside Left Line of Goblin's Hitbox
			isPlayerRightInside = player1.hitbox[0] + player1.hitbox[2] > goblin.hitbox[0]
			if isPlayerTopInside and isPlayerBottomInside:
				if isPlayerLeftInside and isPlayerRightInside:
					player1.hit()
					score -= goblin.damage
		else:
			goblin = Enemy(
				posx = random.randint(10 if score else 15, 20) * 10,
				posy = 400,
				width = 64,
				height = 64,
				health = random.randint(1, 3) * 10,
				end = random.randint(1, 5) * 100 + score//10,
				velocity = random.randint(1, 6) + score//20,
				damage = random.randint(1, 5) * 2 + score//40
			)

			print(f"\
				Goblin Distance from you: {abs(player1.posx - goblin.posx)} \n\
				Goblin Speed: {goblin.velocity} \t\
				Goblin Reach: {goblin.end} \n\
				Goblin Health: {goblin.health} \t\
				Goblin Damage: {goblin.damage} \n")

		if fireratecontroller > 0:
			fireratecontroller += 1
		if fireratecontroller > total_bullets // 2:
			fireratecontroller = 0

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		for i, bullet in reversed(list(enumerate(bullets))):
			if goblin.visible == True:
				# is Top of Bullet inside Bottom Line of Goblin's Hitbox
				isBulletTopInside = bullet.posy - bullet.radius < goblin.hitbox[1] + goblin.hitbox[3]
				# is Bottom of Bullet inside Top Line of Goblin's Hitbox
				isBulletBottomInside = bullet.posy + bullet.radius > goblin.hitbox[1]
				# is Left of Bullet inside Right Line of Goblin's Hitbox
				isBulletLeftInside = bullet.posx - bullet.radius < goblin.hitbox[0] + goblin.hitbox[2]
				# is Right of Bullet inside Left Line of Goblin's Hitbox
				isBulletRightInside = bullet.posx + bullet.radius > goblin.hitbox[0]
				if isBulletTopInside and isBulletBottomInside:
					if isBulletLeftInside and isBulletRightInside:
						hitSound.play()
						goblin.hit(bullet.damage)
						score += 1
						bullets.pop(i)
			if not 0 < bullet.posx < WINX:
				bullets.pop(i)
			else:
				bullet.posx += bullet.velocity

		error_xplus = 10
		error_xminus = 0
		keys = pygame.key.get_pressed()

		if keys[pygame.K_SPACE] and fireratecontroller == 0:
			bulletSound.play()
			if player1.left:
				facing = -1
			else:
				facing = 1
			if len(bullets) < total_bullets:
				bullet = Projectile(round(player1.posx + player1.width // 2), round(player1.posy + player1.height // 2), 6, facing, Color.BLUE.value, 15, 1)
				bullets.append(bullet)
			fireratecontroller += 1

		if keys[pygame.K_LEFT] and player1.posx - player1.velocity + error_xminus >= 0:
			player1.posx -= player1.velocity
			player1.left = True
			player1.right = False
			player1.standing = False
		elif keys[pygame.K_RIGHT] and player1.posx + player1.width + player1.velocity + error_xplus <= WINX:
			player1.posx += player1.velocity
			player1.left = False
			player1.right = True
			player1.standing = False
		else:
			player1.standing = True
			player1.walkCount = 0
			pass

		if keys[pygame.K_UP]:
			player1.isJump = True
		if player1.isJump:
			player1.posy -= jump_velocity
			jump_velocity -= jump_gravity
			if jump_velocity < -jump_height:
				player1.isJump = False
				jump_velocity = jump_height
		else:
			pass

		redrawGameWindow()

	endtime = time.time()

	timeelapsed = endtime - starttime

	win.fill(Color.BLACK.value)
	font = pygame.font.SysFont('comicsans', 16, True)
	if score == 200:
		text = font.render(f"You took {round(timeelapsed, 2)} seconds", 1, Color.RED.value)
	elif score == -200:
		text = font.render(f"Wow, You hit the lowest score possible.", 1, Color.RED.value)
	else:
		text = font.render(f"Thank You for playing the Game.", 1, Color.RED.value)
	win.blit(text, (WINX//2 - (text.get_width()//2), WINY//2))
	pygame.display.update()
	pygame.time.delay(3000)
	print(f"You took {round(timeelapsed, 2)} seconds")
	print("Game Ends...")

	pygame.quit()
