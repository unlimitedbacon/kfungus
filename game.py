class Player():
	bites = 0
	score = 0
	active = False
	alive = True
	panel = None

	def __init__(self, color, name):
		self.color = color
		self.name = name
