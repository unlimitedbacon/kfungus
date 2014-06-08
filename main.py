import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.animation import Animation
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.graphics import Color, Rectangle

from tetrominoes import tetro

Config.set('graphics','width','1280')
Config.set('graphics','height','768')

grid_size_x = 20
grid_size_y = 20

sprite_size = 32

class TetroGrid(GridLayout):
	def setup(self, tetromino):
		self.col_default_width = sprite_size
		self.row_default_height = sprite_size
		self.rows = len(tetromino)
		self.cols = len(tetromino[0])
		self.size = ( sprite_size*self.cols, sprite_size*self.rows )
		for y in range(self.rows):
			for x in range(self.cols):
				b = GridBlock()
				b.background = False
				if tetromino[y][x]:
					b.fungus = 'Green'

					neighbors = ''
					# Up
					if y > 0:
						if tetromino[y-1][x]:
							neighbors = neighbors+'u'
					# Left
					if x > 0:
						if tetromino[y][x-1]:
							neighbors = neighbors+'l'
					# Right
					if x < self.cols-1:
						if tetromino[y][x+1]:
							neighbors = neighbors+'r'
					# Down
					if y < self.rows-1:
						if tetromino[y+1][x]:
							neighbors = neighbors+'d'
					b.neighbors = neighbors

				self.add_widget(b)


class GridBlock(FloatLayout):
	fungus = StringProperty('None')
	neighbors = StringProperty('')
	background = BooleanProperty(True)
	sprite = ObjectProperty(None)
	grid_background = ObjectProperty(None)

	def on_fungus(self, instance, value):
		if value != 'None':
			self.sprite.source = 'atlas://'+value+'/home/x'
		else:
			self.sprite.source = 'blank.png'
	def on_neighbors(self, instance, value):
		if self.fungus != 'None':
			if len(value) > 0:
				self.sprite.source = 'atlas://'+self.fungus+'/home/'+value
			else:
				self.sprite.source = 'atlas://'+self.fungus+'/home/x'
	def on_background(self, instance, value):
		if value:
			self.grid_background.source = 'Grid/block.png'
		else:
			self.grid_background.source = 'blank.png'

class GameGridView(Scatter):
	gglayout = GridLayout(cols = grid_size_x,
			      rows = grid_size_y,
			      col_default_width = sprite_size,
			      row_default_height = sprite_size,
			      padding=0,
			      pos_hint=(None,None),
			      size=( sprite_size*grid_size_x, sprite_size*grid_size_y ))

	def __init__(self, **kwargs):
		super(GameGridView, self).__init__(**kwargs)
		self.size = self.gglayout.size
		self.gglayout.pos = self.pos
		self.add_widget(self.gglayout)

	def setup(self, grid):
		self.gglayout.clear_widgets()
		for y in grid:
			for x in y:
				self.gglayout.add_widget(x)

	def on_touch_down(self, touch):
		if self.parent.collide_point(*touch.pos):
			super(GameGridView, self).on_touch_down(touch)
		if touch.is_double_tap:
			self.center = self.parent.center
			self.scale = 1
		if touch.is_mouse_scrolling:
			if touch.button == 'scrollup':
				self.scale -= 0.1
			else:
				self.scale += 0.1
	
	def on_touch_move(self, touch):
		if self.parent.collide_point(*touch.pos):
			super(GameGridView, self).on_touch_move(touch)

	def global_coords_to_block(self, x, y):
		x, y = self.to_local(x, y)
		# 35 pixels to compensate for GridLayout offset bug
		x = int( x / sprite_size )
		y = int( (self.gglayout.height-y) / sprite_size )
		return x, y

class VertLine(Widget):
	pass

class HorizLine(Widget):
	pass

class Ghost(Scatter):
	def on_touch_up(self, touch):
		super(Ghost, self).on_touch_up(touch)
		#origin = self.parent.player1_panel.center
		#anim = Animation(center=origin)
		#anim.start(self)
		self.parent.place_block(*touch.pos)
		self.parent.remove_widget(self)
	def on_touch_move(self, touch):
		# Snap when inside grid
		g_x, g_y = self.parent.ggview.to_local(*touch.pos)
		s_x, s_y = self.parent.ggview.gglayout.size
		scale = self.parent.ggview.scale
		if g_x > 0 and g_x < s_x and g_y > 0 and g_y < s_y:
			self.x = int(g_x/sprite_size)*sprite_size*scale + self.parent.ggview.x - 34
			self.y = int(g_y/sprite_size)*sprite_size*scale + self.parent.ggview.y - 34
		else:
			self.center = touch.pos 

class NewPieceBox(Widget):
	pass

class PlayerWidget(Widget):
	new_piece_box = ObjectProperty(None)

class FungusGame(FloatLayout):
	grid = []
	player1_panel = ObjectProperty(None)
	ggview = ObjectProperty(None)
	ghost = None

	def new_game(self):
		# Initialize matrix of block objects.
		# Because of the way GridLayout fills itself, coordinates are [Y][X]
		# from top left corner.
		self.grid = []
		for y in range(grid_size_y):
			self.grid.append([])
			for x in range(grid_size_x):
				self.grid[y].append(GridBlock())

		self.grid[5][5].fungus = 'Green'
		self.ggview.setup(self.grid)

		self.player1_panel.new_piece_grid.setup(tetro[3])
	
	def on_touch_down(self, touch):
		super(FungusGame, self).on_touch_down(touch)
		# If player is trying to drag the new piece, generate ghost
		new_piece_box = self.player1_panel.new_piece_box
		if new_piece_box.collide_point(*touch.pos):
			self.ghost = Ghost()
			self.ghost.center = new_piece_box.center
			self.ghost.scale = self.ggview.scale
			self.add_widget(self.ghost)

	def place_block(self, x, y):
		x, y = self.ggview.global_coords_to_block( x, y )
		self.grid[y][x].fungus = 'Green'
		self.update_neighbors(self.grid)
	
	def update_neighbors(self, grid):
		y_len = len(grid)
		x_len = len(grid[0])
		for y in range(y_len):
			for x in range(x_len):
				fungus = grid[y][x].fungus
				if fungus != 'None':
					neighbors = ''
					# Up
					if y > 0:
						if grid[y-1][x].fungus == fungus:
							neighbors = neighbors+'u'
					# Left
					if x > 0:
						if grid[y][x-1].fungus == fungus:
							neighbors = neighbors+'l'
					# Right
					if x < x_len-1:
						if grid[y][x+1].fungus == fungus:
							neighbors = neighbors+'r'
					# Down
					if y < y_len-1:
						if grid[y+1][x].fungus == fungus:
							neighbors = neighbors+'d'
					grid[y][x].neighbors = neighbors

class FungusApp(App):
	def build(self):
		game = FungusGame()
		game.new_game()
		return game

if __name__ == '__main__':
	FungusApp().run()
