def rotate(tetro):
	y_len = len(tetro)
	x_len = len(tetro[0])
	turned = [[0 for x in range(y_len)] for y in range(x_len)]	# Empty matrix with swapped dimensions 
	for ty in range(y_len):						# Start with top row
		for tx in range(x_len):					# Left column moving right
			turned[tx][y_len-ty-1] = tetro[ty][tx]		# Insert into last column moving down
	return turned

