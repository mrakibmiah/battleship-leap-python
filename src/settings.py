import os, inspect

TIME_MODE = 0
TURN_MODE = 1




# Visuals
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FULLSCREEN = False

# Game
WINDOW_TITLE = "Battleships"
GAME_MODE = TURN_MODE
AI_BOMB_INTERVAL = 3000		# time mode only: the time interval in which the AI drops bombs (in ms)
AI_DELAY = 1000				# turn mode only: the timethe AI waits after the player dropped a bomb (in ms)
SHOW_ENEMY_BG = True		# reveals the location of the enemy's ships

# Gameplay
NUM_SQUARES = 10			# number of squares per battleground in each direction. Since battlegrounds are squared,
							# the total number of squares on a battleground equals NUM_FIELDS^2
SHIP_LENS = {6, 5, 4, 3, 2} # the length of each ship on a battleground
NUM_SHIPS = len(SHIP_LENS)	# number of ships per battleground
BOMB_COOLDOWN = 500			# the time interval in that the player can drop a bomb (in ms)




# Internal
SQUARE_DIM = (WINDOW_WIDTH/2 - (WINDOW_WIDTH * 0.1)) / NUM_SQUARES # width/height of a single square in pixels
BG_DIM = SQUARE_DIM * NUM_SQUARES # width/height of one battleground in pixels

SRC_DIR = os.path.dirname(inspect.getfile(inspect.currentframe()))
SOUND_DIR = os.path.join(SRC_DIR, "../data/sounds/")
