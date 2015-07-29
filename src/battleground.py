from square import Square, SquareState
from settings import NUM_SQUARES, SHIP_LENS, SOUND_DIR
import pygame

class Battleground(object):
	def __init__(self, dim):
		#self.squares = [[Square() for j in range(height)] for i in range(width)]
		self.ships = []
		self.dim = dim
		self.missed = []
		self.destroyed_ships = 0

	def add_ship(self, ship):
		"""
		Insert a ship in the battleground.
		:param ship: the ship to insert
		"""
		self.ships.append(ship)


	def check_intersect(self, ship):
		"""
		Check if a ship intercects with any ship on the battleground.
		:param ship: the ship to check
		:return: True if an intersection was found, False otherwise
		"""
		for own_ship in self.ships:
			for square in own_ship.squares:
				for square_other in ship.squares:
					if square_other == square:
						return True
		self.ships.append(ship)
		return False

	def drop_bomb(self, coords):
		"""
		Drop a bomb on the specified coordinates
		:param x: X coordinate of the location where the bomb is to be dropped. Values from 0 to FIELD_DIM
		:param y: Y coordinate of the location where the bomb is to be dropped. Values from 0 to FIELD_DIM
		:returns: whether the bomb missed, hit, or destroyed a ship
		"""
		for ship in self.ships:
			for square in ship.squares:
				if square.x == coords[0] and square.y == coords[1]: # ship was hit
					square.state = SquareState.hit
					print "ship was hit"
					if ship.is_destroyed():
						self.destroyed_ships += 1
						print "and destroyed"
						pygame.mixer.Sound(SOUND_DIR + "/destroy.wav").play()
						if self.destroyed_ships == len(SHIP_LENS):
							print "all Ships are destroyed, GAME OVER"
						return SquareState.destroyed
					pygame.mixer.Sound(SOUND_DIR + "/hit.wav").play()
					return SquareState.hit
		self.missed.append(Square(coords[0], coords[1], SquareState.missed))
		print "nothing was hit"
		pygame.mixer.Sound(SOUND_DIR + "/miss2.wav").play()
		return SquareState.missed

	def get_ship_at(self, coords):
		for ship in self.ships:
			for square in ship.squares:
				if square.x == coords[0] and square.y == coords[1]:
					return ship

	def representation(self):
		squares = [[Square(x, y, SquareState.empty) for x in xrange(NUM_SQUARES)] for y in xrange(NUM_SQUARES)]
		for ship in self.ships:
			destroyed = ship.is_destroyed()
			for square in ship.squares:
				if destroyed:
					squares[square.x][square.y] = Square(square.x, square.y, SquareState.destroyed)
				else:
					squares[square.x][square.y] = square
		for missed in self.missed:
			squares[missed.x][missed.y] = missed
		return squares

	def square_at(self, coords):
		search = Square(coords[0], coords[1], SquareState.empty)
		for ship in self.ships:
			for square in ship.squares:
				if square == search:
					return square
		for square in self.missed:
			if square == search:
				return square
		return search