from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver

class FungusClient(LineReceiver):
	def __init__(self, factory):
		self.factory = factory
		self.game = factory.app.game

	def transmit(self, message):
		# Python 3 workaround
		# Converts unicode strint to byte strings before sending
		# Twisted was written for Python 2, where strings are bytestrings
		# but in Python 3 they are unicode.
		self.sendLine(message.encode("utf-8"))
		print(message)

	def connectionMade(self):
		self.factory.app.on_connection(self)
	
	def lineReceived(self, data):
		data = data.decode("utf-8")
		print(data)

		# Interpret Commands
		# Interrogatives have a ?
		# Imperatives have a :
		if 'USERNAME?' in data:
			name = self.factory.app.config.get('game', 'username')
			self.transmit(name)
		elif 'NUM_PLAYERS?' in data:
			num = self.factory.app.config.get('game', 'num_players')
			self.transmit(num)
		elif 'YOUR_NUM:' in data:
			command, num = data.split(": ")
			num = int(num[0])
			player = self.game.players[num]
			# Enable local control of player
			player.local = True
			# Update name on side panel
			player.name = self.factory.app.config.get('game', 'username')
			player.panel.update( player )
			# Update name on lobby screen
			self.factory.app.lobbyPopup.setSelf( num )
		elif 'NAME:' in data:
			command, options = data.split(": ")
			num, name = options.split(", ")
			num = int(num[0])
			player = self.game.players[num]
			# Update name on side panel
			player.name = name
			player.panel.update( player )
			# Update name on lobby screen
			self.factory.app.lobbyPopup.setName( num, name )
		elif 'START:' in data:
			command, options = data.split(": ")
			start_player, start_piece = options.split(", ")
			start_player = int(start_player[0])
			start_piece = int(start_piece[0])
			self.game.start_game( start_player, start_piece )
			self.factory.app.lobbyPopup.dismiss()
		elif 'PLACE:' in data:
			command, options = data.split(": ")
			x, y = options.split(", ")
			x = int(x)
			y = int(y)
			self.game.place_block(x,y)
		elif 'BITE:' in data:
			command, options = data.split(": ")
			x, y = options.split(", ")
			x = int(x)
			y = int(y)
			self.game.bite_mode = True
			self.game.place_block(x,y)
		elif 'ROT:' in data:
			self.game.new_piece.rotate()
			self.game.update_new_piece_box()			# This could be removed to speed things up
		elif 'TETRO:' in data:
			command, tetro_num = data.split(": ")
			tetro_num = int(tetro_num[0])
			self.game.set_new_piece( tetro_num )
		elif 'ERROR:' in data:
			command, message = data.split(": ")
			self.factory.app.showErrorPopup( 'Notice from server', message )
	
	def sendMove(self, bite_mode, x, y):
		if bite_mode:
			self.transmit( 'BITE: %i, %i' % (x,y) )
		else:
			self.transmit( 'PLACE: %i, %i' % (x,y) )
	
	def sendRot(self):
		self.transmit( 'ROT:' )

# Try protocol.ReconnectingClientFactory to handle lost connections
class NetFactory(protocol.ClientFactory):
	def __init__(self, app):
		self.app = app

	def startedConnecting(self, connector):
		print('Establishing connection')
	
	def buildProtocol(self, addr):
		print('Connected')
		return FungusClient(self)

	def clientConnectionLost(self, connector, reason):
		self.app.showErrorPopup( 'Connection Lost', reason.getErrorMessage() )
		print('Connection Lost')
		print(reason)

	def clientConnectionFailed(self, connector, reason):
		self.app.connectingPopup.dismiss()
		self.app.showErrorPopup( 'Connection Failed', reason.getErrorMessage() )
		print('Connection Failed')
		print(reason)
