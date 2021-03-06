import pygame
import math
import random
from enum import Enum
import sys

pygame.init()

# Game Screen
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Invaders")

# Background
menu_color = pygame.Color('grey12')
background = pygame.image.load("./media/galaxy.png")

# Sound
victory_music_played = False
gameover_music_played = False
pygame.mixer.music.load("./media/menu_background.ogg")
pygame.mixer.music.play(-1)
levelup_sound = pygame.mixer.Sound("./media/level_complete.ogg")
victory_sound = pygame.mixer.Sound("./media/victory.ogg")
gameover_sound = pygame.mixer.Sound("./media/gameover.ogg")
def play_bgmusic():
	if state == State.level_1:
		pygame.mixer.music.load("./media/level1_background.ogg")
	elif state == State.level_2:
		pygame.mixer.music.load("./media/level2_background.ogg")
	elif state == State.level_3:
		pygame.mixer.music.load("./media/level3_background.ogg")
	pygame.mixer.music.play(-1)

# Player
playerImg = pygame.image.load("./media/spaceship.png")
playerX = 370
playerY = 480
playerX_change = 0

# Enemy
enemyImg = []
ufo_image = "./media/ufo.png"
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
total_enemies_killed = 0 # used to change through stages, tracking purposes
enemies_killed = 0 # used to keep track of enemies killed per stage, resets after each stage, display purposes

# Bullet
bulletImg = pygame.image.load("./media/bullet.png")
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 10
bullet_state = "ready"

# Score Board
score_value = 0
font = pygame.font.Font("./fonts/Square.ttf", 24)
textX = 10
textY = 10

# Game Over Text
# create the font for game over
game_over_font = pygame.font.Font("./fonts/Square.ttf", 128)
missioncomplete_font = pygame.font.Font("./fonts/Square.ttf", 75)


def show_score(x, y):
	score = font.render("Score: "+str(score_value), True, (255, 255, 255))
	screen.blit(score, (x, y))

def player(playerImg, x, y):
	screen.blit(playerImg, (x, y))


def enemy(x, y, i): #modify for list of enemies
	screen.blit(enemyImg[i], (x, y))


def create_enemies(num_enemies):
	for i in range(num_enemies): #loop to create # of enemies
		enemyImg.append(pygame.image.load(ufo_image))
		enemyX.append(random.randint(0, 735))
		enemyY.append(random.randint(50, 150))
		enemyX_change.append(4)
		enemyY_change.append(40)

def fire_bullet(x, y):
	global bullet_state

	bullet_state = "fire"
	screen.blit(bulletImg, (x+16, y+10))


def isCollision(enemyX, enemyY, bulletX, bulletY):

	distance = math.sqrt(math.pow(enemyX-bulletX, 2) + math.pow(enemyY-bulletY, 2))

	if distance < 27:
		return True
	else:
		return False

# num_enemies dictate number of enemies per stage
# speed_change dictate speed of enemies per stage
def enemy_movement(num_enemies, speed_change):
	global score_value, bullet_state, bulletX, bulletY, enemyX, enemyY, state, total_enemies_killed, enemies_killed, gameover_music_played

	kill_goal = font.render("Kill "+str(num_enemies)+" aliens to advance to the next level! Speeds will increase!!", True, (255, 255, 255))
	screen.blit(kill_goal, (10, 38))

	create_enemies(num_enemies)
 
	# Enemy Movement
	for i in range(num_enemies): # move every enemy in list
		# Game Over
		if enemyY[i] > 440:  # trigger the end of the game
			pygame.mixer.music.stop()
			if gameover_music_played == False:
				pygame.mixer.Sound.play(gameover_sound)
				gameover_music_played = True
			for j in range(num_enemies):
				enemyY[j] = 2000
			game_over()
			break

		enemyX[i] += enemyX_change[i]
		if enemyX[i] <= 0:
			enemyX_change[i] = speed_change
			enemyY[i] += enemyY_change[i]
		elif enemyX[i] >= 736:
			enemyX_change[i] = -speed_change
			enemyY[i] += enemyY_change[i]

		collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
		if collision:
			total_enemies_killed += 1 # overall tracking purposes
			enemies_killed += 1 # display purposes
			explosion_sound = pygame.mixer.Sound("./media/explosion.wav")
			explosion_sound.play()
			bulletY = 480
			bullet_state = "ready"
			score_value += score_amount
			enemyX[i] = random.randint(0, 800)
			enemyY[i] = random.randint(50, 150)

		kills = font.render("Enemies killed: "+str(enemies_killed), True, (255, 255, 255))
		screen.blit(kills, (150, 10))
		enemy(enemyX[i], enemyY[i], i)

		# State change (to level 2)
		if total_enemies_killed == 2 and state != State.level_2:
			pygame.mixer.stop()
			pygame.mixer.Sound.play(levelup_sound)
			enemies_killed = 0
			state = State.level_2
			score_value += 25
			play_bgmusic()
			
		# State change (to level 3)
		elif total_enemies_killed == 6  and state != State.level_3:
			pygame.mixer.stop()
			pygame.mixer.Sound.play(levelup_sound)
			enemies_killed = 0
			state = State.level_3
			score_value += 25
			play_bgmusic()
			
		# State change (to game over/end)
		elif total_enemies_killed == 12 and state != State.end:
			state = State.end

def game_over():  # display the game over 
	over_font = game_over_font.render("GAME OVER", True, (255, 255, 255))
	screen.blit(over_font, (100, 250))

def playing_background(background):
	# Screen Attributes
	screen.fill((0, 0, 0))
	screen.blit(background, (0, 0))


class State(Enum):
	menu = 1
	play = 2
	end = 3
	level_1 = 4
	level_2 = 5
	level_3 = 6


# Game Loop
state = State.menu
running = True
while running:

	# Game Events
	for event in pygame.event.get():

		if event.type == pygame.QUIT:
			running = False

		# --------- ALL EVENTS / INPUTS ARE IN HERE -------------
		if event.type == pygame.KEYDOWN:

			# if we use menu and end, this will only move/control player in the game, not the menus
			if state is not State.menu and state is not State.end:
				if event.key == pygame.K_LEFT:
					playerX_change = -5

				if event.key == pygame.K_RIGHT:
					playerX_change = 5

				if event.key == pygame.K_SPACE:
					if bullet_state is "ready":
						bullet_sound = pygame.mixer.Sound("./media/laser.wav")
						bullet_sound.play()
						bulletX = playerX
						fire_bullet(bulletX, bulletY)

			elif state is State.menu or state is State.end:
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				# Check for any user input
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						state = State.level_1
						
						#Stops the main screen music when the game begins to play
						pygame.mixer.stop()
						play_bgmusic()
		
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
				playerX_change = 0

	# --------- ALL STATES ARE IN HERE -------------
	if state is State.level_1:
		background = pygame.image.load("./media/earth.png")
		playing_background(background)
		score_amount = 1
		enemy_movement(2, 4) # (num_enemies, speed_change)
		
	elif state is State.level_2:
		newBackground = pygame.image.load("./media/solarSystem.png")
		playing_background(newBackground)
		playerImg = pygame.image.load("./media/pod.png")
		player(playerImg, playerX, playerY)
		score_amount = 5
		enemy_movement(4, 6) # (num_enemies, speed_change)
		
	elif state is State.level_3:
		newBackground = pygame.image.load("./media/galaxy.png")
		playing_background(newBackground)
		playerImg = pygame.image.load("./media/astronaut.png")
		player(playerImg, playerX, playerY)
		score_amount = 10
		enemy_movement(6, 8) # (num_enemies, speed_change)
		
	elif state is State.menu:
		screen.fill(menu_color)

		# Resets scores & name   
		score_value = 0
  
		# Creating the surface for text
		title_text = font.render(f'Space invaders', False, (255, 255, 255))
		start_text = font.render(f'Press enter key to start playing', False, (255, 255, 255))

		screen.blit(title_text, (300, 100))
		screen.blit(start_text, (300, 270))
	elif state is State.end:
		pygame.mixer.music.stop()
		if victory_music_played == False:
			pygame.mixer.Sound.play(victory_sound)
			victory_music_played = True
		game_complete = missioncomplete_font.render("MISSION COMPLETE", True, (255, 255, 255))
		screen.blit(game_complete, (100, 250))

	playerX += playerX_change

	if playerX <= 0:
		playerX = 0
	elif playerX >= 736:
		playerX = 736

	# Bullet Animation
	if bulletY <= 0:
		bulletY = 480
		bullet_state = "ready"

	if bullet_state is "fire":
		fire_bullet(bulletX, bulletY)
		bulletY -= bulletY_change

	player(playerImg, playerX, playerY)
	show_score(textX, textY)

	pygame.display.update()
