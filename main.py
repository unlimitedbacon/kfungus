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
from kivy.properties import ObjectProperty, StringProperty

Config.set('graphics','width','1280')
Config.set('graphics','height','768')

class GridBlock(Widget):
	fungus = StringProperty('None')
	sprite = ObjectProperty(None)
	def on_fungus(self, instance, value):
		if value == 'Green':
			self.sprite.source = 'green/home.png'
		else:
			self.sprite.source = 'blank.png'

class GameGridView(Scatter):
	gglayout = GridLayout(cols=20,
			      rows=20,
			      col_default_width=32,
			      row_default_height=32,
			      size=(32*20,32*20))
	def __init__(self, **kwargs):
		super(GameGridView, self).__init__(**kwargs)
		self.size = self.gglayout.size
		self.add_widget(self.gglayout)
	def setup(self, grid):
		self.gglayout.clear_widgets()
		for x in grid:
			for y in x:
				self.gglayout.add_widget(y)
	def on_touch_down(self, touch):
		super(GameGridView, self).on_touch_down(touch)
		if touch.is_double_tap:
			self.center = self.parent.center
			self.scale = 1
		if touch.is_mouse_scrolling:
			if touch.button == 'scrollup':
				self.scale -= 0.1
			else:
				self.scale += 0.1

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
		self.parent.remove_widget(self)
	def on_touch_move(self, touch):
		self.center = touch.pos

class PlayerWidget(Widget):
	new_piece_box = ObjectProperty(None)
	pass

class FungusGame(FloatLayout):
	grid = []
	player1_panel = ObjectProperty(None)
	ggview = ObjectProperty(None)
	ghost = None

	def new_game(self):
		self.grid = []
		for x in range(20):
			self.grid.append([])
			for y in range(20):
				self.grid[x].append(GridBlock())
		self.grid[5][5].fungus = 'Green'
		self.ggview.setup(self.grid)
	
	def on_touch_down(self, touch):
		super(FungusGame, self).on_touch_down(touch)
		# If player is trying to drag the new piece, generate ghost
		new_piece_box = self.player1_panel.new_piece_box
		if new_piece_box.collide_point(*touch.pos):
			self.ghost = Ghost()
			self.ghost.center = new_piece_box.center
			self.add_widget(self.ghost)

class FungusApp(App):
	def build(self):
		game = FungusGame()
		game.new_game()
		return game

if __name__ == '__main__':
	FungusApp().run()
