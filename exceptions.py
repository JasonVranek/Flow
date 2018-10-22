class InvalidMessageType(Exception):
	"""Raised when a trader submits an ivalid message to the order book""" 
	pass

class NoEntryFound(Exception):
	"""Raised when the order to be cancelled is not found""" 
	pass