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
		self.factory.app.get_message(data)

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
			self.game.players[num].local = True
		elif 'START:' in data:
			command, options = data.split(": ")
			start_player, start_piece = options.split(", ")
			start_player = int(start_player[0])
			start_piece = int(start_piece[0])
			self.game.start_game( start_player, start_piece )
		elif 'ERROR:' in data:
			command, message = data.split(": ")
			self.factory.app.errorPopup( 'Notice from server', message )

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
		self.app.errorPopup( 'Connection Lost', reason.getErrorMessage() )
		print('Connection Lost')
		print(reason)

	def clientConnectionFailed(self, connector, reason):
		self.app.errorPopup( 'Connection Failed', reason.getErrorMessage() )
		print('Connection Failed')
		print(reason)
