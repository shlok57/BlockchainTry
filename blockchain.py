class Blockchain(object):

	def __init__(self):
		self.chain = []
		self.currentTransaction = []

		# Create the first block
		

	def newBlock(self):
		pass

	def newTransaction(self, sender, recipient, amount):
		"""
		Creates a new transaction to go into next mined block

		:param sender:		<str>	Address of the sender
		:param recipient:	<str>	Address of the recipient
		:param amount:		<int>	Amount of the transaction
		:return:			<int>	index of the block holding the transaction
		"""
		
		self.currentTransaction.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
		})

		return self.lastBlock['index'] + 1

	@staticmethod
	def hash(block):
		pass

	@property
	def lastBlock(self):
		pass