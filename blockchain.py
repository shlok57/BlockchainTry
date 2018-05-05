import hashlib
import json
from time import time

class Blockchain(object):

	def __init__(self):
		self.chain = []
		self.currentTransactions = []

		# Create the first block
		self.newBlock(previousHash=1, proof=100)


	def newBlock(self, proof, previousHash=None):
		"""
		Cretes a new block in the Blockchain

		:param previousHash:	<str>	Hash of the previous Block (Optional)
		:param proof:			<int>	Proof given by Proof of work algorithm
		:return: 				<dict>	New Block 
		"""
		
		block = {
			'index': len(self.chain) + 1,
			'timestamp': time(),
			'transactions': self.currentTransactions,
			'proof': proof,
			'previousHash': previousHash or self.hash(self.chain[-1]),
		}

		self.currentTransactions = []
		self.chain.append(block)

		return block


	def newTransaction(self, sender, recipient, amount):
		"""
		Creates a new transaction to go into next mined block

		:param sender:		<str>	Address of the sender
		:param recipient:	<str>	Address of the recipient
		:param amount:		<int>	Amount of the transaction
		:return:			<int>	index of the block holding the transaction
		"""
		
		self.currentTransactions.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
		})

		return self.lastBlock['index'] + 1


	@staticmethod
	def hash(block):
		"""
		Creates a SHA256 hash of a block

		:param block:	<dict>	a Block
		:return:		<str> SHA256 of the block
		"""

		blockStr = json.dumps(block, sort_keys:True).encode()

		return hashlib.sha256(blockStr).hexdigest()


	@property
	def lastBlock(self):
		"""
		the last block of the blockchain
		"""