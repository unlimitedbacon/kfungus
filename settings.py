import json

settings_json = json.dumps([
	{'type': 'options',
	 'title': 'Number of Players',
	 'desc': 'Number of players',
	 'section': 'game',
	 'key': 'num_players',
	 'options': ['2', '3', '4'] }])
