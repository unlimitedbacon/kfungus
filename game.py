grid_size_x = 20
grid_size_y = 20

anim_speed = 0.2

class Player():
	color = ''
	name = ''
	home = [0,0]
	bites = 5
	score = 0
	active = False
	alive = True
	panel = None

	def __init__(self, color, name, home):
		self.color = color
		self.name = name
		self.home = home

class Grid(list):
	def place_block(self, new_piece, color, x, y):
		t_height = len(new_piece)
		t_width = len(new_piece[0])
		# Check boundries
		if (y<0) or (x<0):
			return False
		if ( y+t_height > grid_size_y ) or ( x+t_width > grid_size_x ):
			return False
		# Check for Collisions
		for ty in range(t_height):
			for tx in range(t_width):
				if new_piece[ty][tx]:
					if self[y+ty][x+tx].fungus != 'None':
						# Stop here and do not place piece
						# Might be better to raise an exception
						return False
		# Check for contact with team
		contact = False
		for ty in range(t_height):
			for tx in range(t_width):
				if new_piece[ty][tx]:
					# Check above current space
					if (y+ty-1) >= 0:		# Make sure your not checking a nonexistent space
						cell_above = self[y+ty-1][x+tx]
						if cell_above.fungus == color:
							contact = True
					# Below
					if (y+ty+1) < 20:
						cell_below = self[y+ty+1][x+tx]
						if cell_below.fungus == color:
							contact = True
					# Left
					if (x+tx-1) >=0:
						cell_left = self[y+ty][x+tx-1]
						if cell_left.fungus == color:
							contact = True
					# Right
					if (x+tx+1) < 20:
						cell_right = self[y+ty][x+tx+1]
						if cell_right.fungus == color:
							contact = True
		if contact == False:
			return False
		# Copy new piece onto game grid
		for ty in range(t_height):
			for tx in range(t_width):
				if new_piece[ty][tx]:
					self[y+ty][x+tx].fungus = color
		# Run eat() for each new square
		for ty in range(t_height):
			for tx in range(t_width):
				if new_piece[ty][tx]:
					self.eat( color, x+tx, y+ty )
		self.update_neighbors()
		return True

	def eat(self, color, x, y):
		# Start with a single square
		# Cast rays in all 8 direction (up,dwn,lft,rght,diag)
		# if ray encounters team member, all squares along ray are eaten
		# eat() is called for all converted squares
		ray_vectors =  [[ -1, 0 ],				# [ Y, X ]
				[ -1, 1 ],
				[  0, 1 ],
				[  1, 1 ],
				[  1, 0 ],
				[  1,-1 ],
				[  0,-1 ],
				[ -1,-1 ]]
		
		for vector in ray_vectors:
			ray_len = 1
			ray_end_y = y + vector[0]
			ray_end_x = x + vector[1]
			if self.in_bounds(ray_end_x,ray_end_y):
				ray_end_fungus = self[ ray_end_y ][ ray_end_x ].fungus
			else:
				ray_end_fungus = 'None'
			# Ray will continue firing until it reaches the end of the grid, an empty space,
			# a team mate, or the team leader
			while ray_end_fungus != 'None' and ray_end_fungus != color:
				ray_len += 1
				ray_end_y += vector[0]
				ray_end_x += vector[1]
				if self.in_bounds(ray_end_x,ray_end_y):
					ray_end_fungus = self[ ray_end_y ][ ray_end_x ].fungus
				else:
					ray_end_fungus = 'None'
			if ray_end_fungus == color:
				# Do something here that makes them all turn colors
				for victim in range(1,ray_len):
					victim_y = y + vector[0] * victim
					victim_x = x + vector[1] * victim
					self[victim_y][victim_x].fungus = color
					self.eat(color,victim_x,victim_y)
	
	def phone_home(self, player, imperial_map, x, y):
		imperial_map[y][x] = True
		if y-1 >= 0:
			if self[y-1][x].fungus == player.color and imperial_map[y-1][x] == False:
				self.phone_home( player, imperial_map, x, y-1 )
		if y+1 < 20:
			if self[y+1][x].fungus == player.color and imperial_map[y+1][x] == False:
				self.phone_home( player, imperial_map, x, y+1 )
		if x-1 >= 0:
			if self[y][x-1].fungus == player.color and imperial_map[y][x-1] == False:
				self.phone_home( player, imperial_map, x-1, y )
		if x+1 < 20:
			if self[y][x+1].fungus == player.color and imperial_map[y][x+1] == False:
				self.phone_home( player, imperial_map, x+1, y )
	
	def imperial_census(self, players):
		# For all teams
		# Check to make sure each thing is somehow
		# connected to the home base
		# If not, it dies.
		for empire in players:
			imperial_map = [[False for x in range(grid_size_x)] for y in range(grid_size_y)]
			self.phone_home( empire, imperial_map, empire.home[1], empire.home[0] )
			# Compare game grid against map to find independents
			for y in range(0,grid_size_y):
				for x in range(0,grid_size_x):
					if self[y][x].fungus == empire.color and imperial_map[y][x] == False:
						self[y][x].fungus = 'None'

	def update_neighbors(self):
		y_len = len(self)
		x_len = len(self[0])
		for y in range(y_len):
			for x in range(x_len):
				fungus = self[y][x].fungus
				if fungus != 'None':
					neighbors = ''
					# Up
					if y > 0:
						if self[y-1][x].fungus == fungus:
							neighbors = neighbors+'u'
					# Left
					if x > 0:
						if self[y][x-1].fungus == fungus:
							neighbors = neighbors+'l'
					# Right
					if x < x_len-1:
						if self[y][x+1].fungus == fungus:
							neighbors = neighbors+'r'
					# Down
					if y < y_len-1:
						if self[y+1][x].fungus == fungus:
							neighbors = neighbors+'d'
					self[y][x].neighbors = neighbors

	def in_bounds(self, x, y):
		if y >= 0 and y < grid_size_y and x >= 0 and x < grid_size_x:
			return True
		else:
			return False
	
	def kill(self, loser):
		# Delete all of a players remaining blocks
		for y in range(grid_size_y):
			for x in range(grid_size_x):
				if self[y][x].fungus == loser.color:
					self[y][x].fungus = 'None'
	
	def bite(self, player, x, y):
		# Make sure player has enough bites
		if player.bites <= 0:
			return False
		# Check boundries
		if not self.in_bounds(x,y):
			return False
		# Check to make sure cell isn't empty or your own team
		if self[y][x].fungus == 'None' or self[y][x].fungus == player.color:
			return False
		# This part is copied from place()
		# it should probably be put in its own function
		# Check for contact with team
		contact = False
		# Check above current space
		if (y+ty-1) >= 0:		# Make sure your not checking a nonexistent space
			cell_above = self[y+ty-1][x+tx]
			if cell_above.fungus == color:
				contact = True
		# Below
		if (y+ty+1) < 20:
			cell_below = self[y+ty+1][x+tx]
			if cell_below.fungus == color:
				contact = True
		# Left
		if (x+tx-1) >=0:
			cell_left = self[y+ty][x+tx-1]
			if cell_left.fungus == color:
				contact = True
		# Right
		if (x+tx+1) < 20:
			cell_right = self[y+ty][x+tx+1]
			if cell_right.fungus == color:
				contact = True
		if contact == False:
			return False
		# Take a bite
		self[y][x].fungus = 'None'
		player.bites -= 1

