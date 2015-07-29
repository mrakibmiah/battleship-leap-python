from square import SquareState

class Ship(object):
	def __init__(self, size):
		self.squares = [size]

	def is_destroyed(self):
		for square in self.squares:
			if square.state == SquareState.intact:
				return False
		return True