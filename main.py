import kivy
kivy.require('1.8.0')

from random import randint

from kivy.app import App
from kivy.config import Config
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.settings import SettingsWithSidebar
from kivy.animation import Animation
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.graphics import Color, Rectangle

from tetrominoes import tetros
from game import *
from settings import settings_json

# Set window to same resolution as Nexus 4
#Config.set('graphics','width','1280')
#Config.set('graphics','height','768')

sprite_size = 32

# Shows a single lonesome tetromino
class TetroGrid(GridLayout):
	def setup(self, tetromino, fungus, ftype='norm'):
		self.clear_widgets()
		self.col_default_width = sprite_size
		self.row_default_height = sprite_size
		self.rows = len(tetromino)
		self.cols = len(tetromino[0])
		self.size = ( sprite_size*self.cols, sprite_size*self.rows )
		# Add each block to the GridLayout
		for y in range(self.rows):
			for x in range(self.cols):
				b = GridBlock()
				b.background = False
				b.ftype = ftype
				if tetromino[y][x]:
					b.fungus = fungus

					# Join neighboring blocks
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


# A single grid block containing either a fungus or nothing
class GridBlock(FloatLayout):
	fungus = StringProperty('None')
	ftype = StringProperty('norm')
	neighbors = StringProperty('')
	background = BooleanProperty(True)
	sprite = ObjectProperty(None)
	grid_background = ObjectProperty(None)
	sammich = BooleanProperty(False)

	def on_fungus(self, instance, value):
		self.update_sprite()
	def on_sammich(self, instance, value):
		self.update_sprite()
	def on_ftype(self, instance, value):
		self.update_sprite()
	def on_neighbors(self, instance, value):
		self.update_sprite()
	def on_background(self, instance, value):
		if value:
			self.grid_background.source = 'Graphics/Grid/block.png'
		else:
			self.grid_background.source = 'Graphics/blank.png'
	def update_sprite(self):
		if self.fungus == 'None':
			if self.sammich:
				self.sprite.source = 'Graphics/sammich.png'
			else:
				self.sprite.source = 'Graphics/blank.png'
		else:
			if self.neighbors == '':
				self.sprite.source = 'atlas://Graphics/'+self.fungus+'/'+self.ftype+'/x'
			else:
				self.sprite.source = 'atlas://Graphics/'+self.fungus+'/'+self.ftype+'/'+self.neighbors

# Drag and zoomable view of the entire game grid
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
		x = int( x / sprite_size )
		y = int( (self.gglayout.height-y) / sprite_size )
		return x, y

# Layout dividers
class VertLine(Widget):
	pass
class HorizLine(Widget):
	pass

# Outline showing where new blocks will be placed
class Ghost(Scatter):
	ghost_grid = ObjectProperty(None)

	def setup(self, np, color):
		self.ghost_grid.setup( np, color, 'ghost' )
		self.ghost_grid.y = sprite_size - self.ghost_grid.height
			
	def on_touch_up(self, touch):
		super(Ghost, self).on_touch_up(touch)
		scale = self.parent.ggview.scale
		t_x = touch.x - self.ghost_grid.cols*sprite_size*scale
		t_y = touch.y + self.ghost_grid.rows*sprite_size*scale
		x, y = self.parent.ggview.global_coords_to_block( t_x, t_y )
		self.parent.place_block( x, y )
		self.parent.remove_widget(self)

	def on_touch_move(self, touch):
		# Snap when inside grid
		g_x, g_y = self.parent.ggview.to_local(*touch.pos)
		s_x, s_y = self.parent.ggview.gglayout.size
		scale = self.parent.ggview.scale
		if g_x > sprite_size and g_x < s_x+sprite_size and g_y > -sprite_size and g_y < s_y-sprite_size:
			self.x = (g_x//sprite_size-self.ghost_grid.cols)*sprite_size*scale + self.parent.ggview.x
			self.y = (g_y//sprite_size+self.ghost_grid.rows)*sprite_size*scale + self.parent.ggview.y
		else:
			self.x = touch.x - self.width - sprite_size
			self.y = touch.y + self.ghost_grid.rows*sprite_size

class NewPieceBox(Widget):
	grid = ObjectProperty(None)

class PlayerWidget(Widget):
	icon = ObjectProperty(None)
	name_label = ObjectProperty(None)
	bites_grid = ObjectProperty(None)

	def update(self, player):
		self.bites_grid.clear_widgets()
		for x in range(player.bites):
			self.bites_grid.add_widget( Image(source='atlas://Graphics/Bite/norm/x') )

class ButtonsGrid(BoxLayout):
	pass

class FungusGame(FloatLayout):
	side_panel = ObjectProperty(None)
	ggview = ObjectProperty(None)
	#new_piece_box = ObjectProperty(None)
	ghost = None
	grid = Grid()
	players = []
	curr_player_num = 0
	new_piece = tetros[0]
	bite_mode = False

	def new_game(self, num_players):
		# Clear everything
		self.grid = Grid()
		self.side_panel.clear_widgets()
		# Setup players
		if num_players == '4':
			self.players = [ Player(  'Green', 'Algae',       [ 5, 5 ] ),
					 Player(    'Red', 'E Coli',      [ 5, grid_size_x-6 ] ),
					 Player(   'Blue', 'Nanites',     [ grid_size_y-6, grid_size_x-6 ] ),
					 Player( 'Yellow', 'Penicillium', [ grid_size_y-6, 5 ] )]
		elif num_players == '3':
			self.players = [ Player(  'Green', 'Algae',       [ 5, 5 ] ),
					 Player(    'Red', 'E Coli',      [ 5, grid_size_x-6 ] ),
					 Player(   'Blue', 'Nanites',     [ grid_size_y-6, grid_size_x-6 ] )]
		else:
			self.players = [ Player(  'Green', 'Algae',       [ 5, 5 ] ),
					 Player(   'Blue', 'Nanites',     [ grid_size_y-6, grid_size_x-6 ] )]
		# Initialize player widgets and add them to the side panel
		for n in range(len(self.players)):
			p = self.players[n]
			p.panel = PlayerWidget()
			p.panel.name_label.text = p.name
			p.panel.icon.source = 'atlas://Graphics/'+p.color+'/home/x'
			p.panel.update( p )
			self.side_panel.add_widget( p.panel )
			# Add dividers
			if n < len(self.players)-1:
				self.side_panel.add_widget( HorizLine() )
		# Add box and buttons to side panel
		self.new_piece_box = NewPieceBox()
		self.side_panel.add_widget( self.new_piece_box )
		self.side_panel.add_widget( ButtonsGrid() )
		# Choose random starting player
		self.curr_player_num = randint( 0, len(self.players)-1 )
		self.curr_player = self.players[ self.curr_player_num ]
		# Initialize matrix of block objects.
		# Because of the way GridLayout fills itself, coordinates are [Y][X]
		# from top left corner.
		for y in range(grid_size_y):
			self.grid.append([])
			for x in range(grid_size_x):
				self.grid[y].append(GridBlock())

		# Add home blocks
		for player in self.players:
			self.grid[ player.home[0] ][ player.home[1] ].fungus = player.color
			self.grid[ player.home[0] ][ player.home[1] ].ftype = 'home'

		# Add Sandwiches in corners
		self.grid[ 0 ][ 0 ].sammich = True
		self.grid[ 0 ][ grid_size_x-1 ].sammich = True
		self.grid[ grid_size_y-1 ][ 0 ].sammich = True
		self.grid[ grid_size_y-1 ][ grid_size_x-1 ].sammich = True

		self.ggview.setup(self.grid)

		# Choose random starting piece
		self.new_piece = tetros[ randint(0,9) ]

		self.update_new_piece_box()
	
	def on_touch_down(self, touch):
		super(FungusGame, self).on_touch_down(touch)
		# If player is trying to drag the new piece, generate ghost
		if self.new_piece_box.collide_point(*touch.pos):
			self.ghost = Ghost()
			self.ghost.center = self.new_piece_box.center
			self.ghost.scale = self.ggview.scale
			if self.bite_mode:
				self.ghost.setup( [[True]], 'Bite' )
			else:
				self.ghost.setup( self.new_piece, self.curr_player.color )
			self.add_widget(self.ghost)
	
	def on_touch_up(self, touch):
		super(FungusGame, self).on_touch_up(touch)
		# If player taps the box, rotate new piece
		if self.new_piece_box.collide_point(*touch.pos):
			self.rotate_new_piece()
	
	def rotate_new_piece(self):
		self.new_piece.rotate()
		self.update_new_piece_box()

	def place_block(self, x, y):
		if self.bite_mode:
			r = self.grid.bite( self.curr_player, x, y )
			if r:
				self.toggle_bite_mode()
		else:
			r = self.grid.place_block( self.new_piece, self.curr_player, x, y )
		if r:
			self.check_pulse()
			self.grid.imperial_census( self.players )
			self.curr_player.panel.update( self.curr_player )
			self.next_turn()
	
	def toggle_bite_mode(self):
		self.bite_mode = not self.bite_mode
		self.update_new_piece_box()
	
	def next_turn(self):
		self.curr_player_num += 1
		if self.curr_player_num >= len(self.players):
			self.curr_player_num = 0
		self.curr_player = self.players[ self.curr_player_num ]
		self.new_piece = tetros[ randint(0,9) ]
		self.update_new_piece_box()
	
	def check_pulse(self):
		# Check to make sure the head of each team is alive
		# if not, remove them from the players list
		# and delete the rest of their blocks
		#for x in range(len(self.players)):
		#	patient = self.players[x]
		for patient in self.players:
			home_fungus = self.grid[ patient.home[0] ][ patient.home[1] ].fungus
			if home_fungus != patient.color:
				self.grid.kill(patient)
				self.side_panel.remove_widget( patient.panel )
				self.players.remove(patient)
	
	def update_new_piece_box(self):
		box = self.new_piece_box
		if self.bite_mode:
			box.grid.setup( [[True]], 'Bite' )
		else:
			box.grid.setup( self.new_piece, self.curr_player.color )
	
	
class FungusApp(App):
	def build(self):
		self.icon = 'icon.png'
		#self.use_kivy_settings = False
		self.game = FungusGame()
		self.game.new_game( self.config.get('game', 'num_players') )
		return self.game
	
	def build_config(self, config):
		config.setdefaults('game', {'num_players': '4' })
		config.setdefaults('graphics', {'width': 1280,
				   		'height': 768})
	
	def build_settings(self, settings):
		settings.add_json_panel('Game Settings',
					self.config,
					data=settings_json)
	
	def on_config_change(self, config, section, key, value):
		if key == 'num_players':
			self.game.new_game(value)

if __name__ == '__main__':
	app = FungusApp()
	app.run()
