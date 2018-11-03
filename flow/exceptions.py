class InvalidMessageType(Exception):
	'''Raised when a trader submits an ivalid message to the order book''' 
	pass

class NoEntryFound(Exception):
	'''Raised when the order to be cancelled is not found''' 
	pass

class InvalidMessageParameter(Exception):
	'''Raised when the order contains parameters of the wrong type'''
	pass

class NoOrderToUpdate(Exception):
	'''Raised when a trader tries to update a message but hasn't send a message before'''
	pass

class NoOrderToCancel(Exception):
	'''Raised when a trader tries to cancel a message but hasn't send a message before'''
	pass