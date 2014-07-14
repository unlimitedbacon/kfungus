from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver

class FungusClient(LineReceiver):
	def __init__(self, factory):
		self.factory = factory

	def transmit(self, message):
		# Python 3 workaround
		# Converts unicode strint to byte strings before sending
		# Twisted was written for Python 2, where strings are bytestrings
		# but in Python 3 they are unicode.
		self.sendLine(message.encode("utf-8"))

	def connectionMade(self):
		self.factory.app.on_connection(self)
	
	def lineReceived(self, data):
		self.factory.app.get_message(data)

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
