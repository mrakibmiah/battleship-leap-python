import os
import inspect
import sys
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
lib_dir = os.path.abspath(os.path.join(src_dir, "../lib/enum34-1.0.4"))
sys.path.insert(0, lib_dir)
from enum import Enum

class SquareState(Enum):
	empty 		= 1 # square is neither part of a ship nor was a bomb dropped on it
	missed 		= 2 # square is not part of a ship and a bomb was dropped on it
	hit			= 3 # square is part of a ship and was hit
	intact 		= 4 # square is part of a ship and is intact
	destroyed 	= 5 # square is part of a destroyed ship

class Square(object):
	def __init__(self, x, y, state):
		self.state = state
		self.y = y
		self.x = x

	def __eq__(self, other):
		"""
		Override the comparison operator. Two squares are equal when their respective x and y values match. The state
		of the square is disregarded
		:param other: the comparee
		:return: True if the squares are sementically equal, False otherwise
		"""
		return self.x == other.x and self.y == other.y

	class __metaclass__(type):
		def __iter__(self):
			for attr in dir(Square):
				if not attr.startswith("__"):
					yield attr