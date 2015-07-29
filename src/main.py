#!/usr/bin/python
from settings import *
import os
import sys
lib_dir = os.path.abspath(os.path.join(SRC_DIR, "../lib/LeapSDK"))
sys.path.insert(0, lib_dir)
import Leap
import pygame
from battleground import Battleground
from square import Square, SquareState
from ship import Ship
import random


class Game:

	def __init__(self):
		"""
		Initialize the game.
		"""
		self.setup_window()
		self.controller = Leap.Controller()
		self.bg_player = Battleground(NUM_SQUARES) # the player's battleground
		self.bg_comp = Battleground(NUM_SQUARES) # the opponent's battleground
		self.populate_bg(self.bg_comp)
		self.populate_bg(self.bg_player)
		y_offset = (WINDOW_HEIGHT - BG_DIM) / 2
		x_offset = (WINDOW_WIDTH - BG_DIM * 2) / 4
		# top left corner positions of the respective battlegrounds:
		self.bg_player_x = x_offset
		self.bg_player_y = self.bg_comp_y = y_offset
		self.bg_comp_x = WINDOW_WIDTH - BG_DIM - x_offset
		#self.touch_distance = 0
		self.bomb_cooldown = BOMB_COOLDOWN

		self.forget = [] 	# list of squares that missed or belong to sunken ships
		self.hits = []
		self.comp_turn = False

	def reset(self):
		self.bg_player = Battleground(NUM_SQUARES)
		self.bg_comp = Battleground(NUM_SQUARES)
		self.populate_bg(self.bg_comp)
		self.populate_bg(self.bg_player)

	def populate_bg(self, bg):
		"""
		Populate a battleground with random ships.
		:param bg: the battleground to populate
		"""
		it = SHIP_LENS.__iter__()
		ship_len = it.next()
		while True:
		#for ship_len in SHIP_LENS:
			ship = Ship(ship_len)
			direction = random.randint(0, 1) # 0 = vertical, 1 = horizontal
			if direction == 0:
				start_x = random.randint(0, NUM_SQUARES - 1)
				start_y = random.randint(0, NUM_SQUARES - 1 - ship_len)
			elif direction == 1:
				start_x = random.randint(0, NUM_SQUARES - 1 - ship_len)
				start_y = random.randint(0, NUM_SQUARES - 1)

			squares = []
			for i in xrange(ship_len):
				if direction == 0:
					squares.append(Square(start_x, start_y + i, SquareState.intact))
				elif direction == 1:
					squares.append(Square(start_x + i, start_y, SquareState.intact))

			ship.squares = squares
			if bg.check_intersect(ship):
				continue
			bg.add_ship(ship)

			# Python's fucked up way to check if an iterator reached the end of a container
			try:
				ship_len = it.next()
			except:
				break

	def setup_window(self):
		"""
		Initialize the window.
		"""
		pygame.init()
		if FULLSCREEN:
			self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
		else:
			self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
		pygame.display.set_caption(WINDOW_TITLE)

	def resolve_position(self, x, y):
		"""
		Resolve the cursor position to a battleground
		:param x: X value of the cursor position in pixels
		:param y: Y value of the cursor position in pixels
		:return: the battleground, or nothing if no battleground was found
		"""
		if self.bg_comp_x <= x <= self.bg_comp_x + BG_DIM:
			if self.bg_comp_y <= y <= self.bg_comp_y + BG_DIM:
				return self.bg_comp
		elif self.bg_player_x <= x <= self.bg_player_x + BG_DIM:
			if self.bg_player_y <= y <= self.bg_player_y + BG_DIM:
				return self.bg_player

	def draw_bg(self, bg, x_offset, y_offset):
		"""
		Draw a battleground at a certain position of the screen
		:param bg: the battleground to draw
		:param x_offset: the x-offset from the left border of the screen
		:param y_offset: the y-offset from the top border of the screen
		:return: nothing
		"""
		field = bg.representation()
		for y in range(NUM_SQUARES):
			for x in range(NUM_SQUARES):
				square = field[x][y]
				if square.state == SquareState.hit:
					color = pygame.Color("orange")
				elif square.state == SquareState.missed:
					color = pygame.Color("purple")
				elif square.state == SquareState.destroyed:
					color = pygame.Color("red")
				elif square.state == SquareState.intact:# and bg == self.bg_player:
					color = pygame.Color("grey") # show ship location for debugging purposes
				else:
					color = pygame.Color(57, 145, 208)

				rect = (x * SQUARE_DIM + x_offset, y * SQUARE_DIM + y_offset, SQUARE_DIM, SQUARE_DIM)
				pygame.draw.rect(self.window, color, rect)
				pygame.draw.rect(self.window, pygame.Color("grey"), rect, 2)

	def handle_leap(self):
		"""
		Interpret the input received from the leap motion controller and translate the input to mouse output.
		Pointing translates to mouse movements and thrusting towards the screen translates to mouse clicks.
		:return: nothing
		"""
		if self.controller.is_connected:
			frame = self.controller.frame()
			pointable = frame.pointables.frontmost
			if pointable.is_valid:
				i_box = frame.interaction_box
				leap_point = pointable.stabilized_tip_position
				normalized_point = i_box.normalize_point(leap_point)
				normalized_point *= 1.5
				normalized_point -= Leap.Vector(.25, .25, .25)
				cursor_x = int(normalized_point.x * WINDOW_WIDTH)
				cursor_y = int((1 - normalized_point.y) * WINDOW_HEIGHT)
				pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, {'pos': (cursor_x, cursor_y)}))

				# detect thrust
				#prev_dist = self.touch_distance
				vel = pointable.tip_velocity.z
				#new_dist = pointable.touch_distance
				#delta = prev_dist - new_dist
				#if delta > 0.05 and self.bomb_cooldown >= BOMB_COOLDOWN:
				if vel < -50 and self.bomb_cooldown >= BOMB_COOLDOWN:
					# drop bomb
					pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (cursor_x, cursor_y)}))
					self.bomb_cooldown = 0
				#self.touch_distance = new_dist
				time_diff = (frame.timestamp - self.controller.frame(1).timestamp) / 1000
				self.bomb_cooldown += time_diff

	def ai_drop_bomb(self, bg, coords):
		status = bg.drop_bomb(coords)
		if status == SquareState.missed:
			self.forget.append(coords)
		elif status == SquareState.destroyed:
			ship = bg.get_ship_at(coords)
			for destroyed in ship.squares:
				coords = (destroyed.x, destroyed.y)
				self.forget.append(coords)
				for c in self.hits:
					if c[0] == coords[0] and c[1] == coords[1]:
						self.hits.remove(c)
		elif status == SquareState.hit:
			self.hits.append(coords)

	def decide_action(self, bg):
		if len(self.hits) == 0:
			square = (random.randint(0, NUM_SQUARES-1), random.randint(0, NUM_SQUARES-1))
			while True:
				square = (random.randint(0, NUM_SQUARES-1), random.randint(0, NUM_SQUARES-1))
				if square not in self.forget:
					break
			self.ai_drop_bomb(bg, square)
		else:
			for hit in self.hits:
				tries = 0
				direction = random.randint(0, 3) # 0=up, 1=right, 2=down, 4=left
				while True:
					if direction == 0: 		target = (hit[0], hit[1] - 1)
					elif direction == 1: 	target = (hit[0] + 1, hit[1])
					elif direction == 2: 	target = (hit[0], hit[1] + 1)
					else: 					target = (hit[0] - 1, hit[1])

					if 0 <= target[0] < NUM_SQUARES and 0 <= target[1] < NUM_SQUARES:
						if target not in self.forget and target not in self.hits:
							self.ai_drop_bomb(bg, target)
							return
					tries += 1
					if tries == 4:
						break
					direction = (direction + 1) % 4

	def run(self):
		"""
		Main loop: called several times per second, handles events
		:return: nothing
		"""
		self.window.fill((20, 20, 20))
		self.draw_bg(self.bg_player, self.bg_player_x, self.bg_player_y)
		self.draw_bg(self.bg_comp, self.bg_comp_x, self.bg_comp_y)

		self.handle_leap()

		if self.comp_turn:
			self.decide_action(self.bg_player)
			self.comp_turn = False

		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.event.post(pygame.event.Event(pygame.QUIT))
				elif event.key == pygame.K_F1:
					self.reset()
			elif event.type == pygame.QUIT:
				sys.exit(0)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				cursor_x, cursor_y = event.pos
				bg = self.resolve_position(cursor_x, cursor_y)
				if(bg == self.bg_comp):
					x_coord = int((cursor_x - self.bg_comp_x) / SQUARE_DIM)
					y_coord = int((cursor_y - self.bg_comp_y) / SQUARE_DIM)
					coords = (x_coord, y_coord)
					square = bg.square_at(coords)
					if square.state == SquareState.empty or square.state == SquareState.intact:
						bg.drop_bomb(coords)
						self.comp_turn = True
			else:
				app_x, app_y = pygame.mouse.get_pos()
				if event.type == pygame.MOUSEMOTION:
					app_x, app_y = event.pos
				#radius = int(self.touch_distance * 30)
				#radius = max(min(radius, 15), 4)
				radius = 10
				pygame.draw.circle(self.window, (255, 255, 255), (app_x, app_y), radius , 2)
				pygame.display.flip()

game = Game()
def main():
	while True:
		game.run()

if __name__ == '__main__':
	main()