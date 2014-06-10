class Tetro(list):
	def rotate(self):
		y_len = len(self)
		x_len = len(self[0])
		turned = [[0 for x in range(y_len)] for y in range(x_len)]	# Empty matrix with swapped dimensions 
		for ty in range(y_len):						# Start with top row
			for tx in range(x_len):					# Left column moving right
				turned[tx][y_len-ty-1] = self[ty][tx]		# Insert into last column moving down
		print(turned)
		self.__init__(turned)

# Dictionary of tetrominoes
tetros = { 0: Tetro([[ True ]]),				# 0:	#

	   1: Tetro([[ True, True, True, True ]]),		# 1:	# # # #

	   2: Tetro([[ True, False, False ],			# 2:	#
		     [ True,  True, True  ]]),			#   	# # #

	   3: Tetro([[ False, False, True ],			# 3:	    #
		     [  True,  True, True ]]),			#   	# # #

	   4: Tetro([[ False, True,  True ],			# 4:	  # #
		     [  True, True, False ]]),			#   	# #

	   5: Tetro([[  True, True, False ],			# 5:	# #
		     [ False, True,  True ]]),			#   	  # #

	   6: Tetro([[ True, True, ],				# 6:	# #
		     [ True, True, ]]),				#   	# #

	   7: Tetro([[ False, True, False ],			# 7:	  #
		     [  True, True,  True ]]),			#   	# # #

	   8: Tetro([[ True, False ],				# 8:	#
		     [ True,  True ]]),				#   	# #

	   9: Tetro([[ True, True ]])				# 9:	# #
	}
