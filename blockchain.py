import hashlib
import json

from time import time
from uuid import uuid4


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


	def proofOfWork(self, lastProof):
		"""
		Proof of Work Algorothm:
			- Search for a number q such that hash(p,q) has 4 leading 0's, where p is the previous q
			- p is the previous proof, q is the new proof

		:param lastProof:	<int>	Last proof generated
		:return:			<int>	New proof generated
		"""

		proof = 0

		while !validProof(proof, lastProof):
			proof += 1

		return proof



	@staticmethod
	def hash(block):
		"""
		Creates a SHA256 hash of a block

		:param block:	<dict>	a Block
		:return:		<str> SHA256 of the block
		"""

		blockStr = json.dumps(block, sort_keys:True).encode()

		return hashlib.sha256(blockStr).hexdigest()


	@staticmethod
	def validProof(proof, lastProof):
		"""
		Validates the proof against lastProof
			- hash(proof,lastProof) should have 4 leading 0's

		:param proof:		<int>	proof to validated
		:param lastProof:	<int>	last proof generated
		:return:			<Bool>	True iff proof is valid, False otherwise
		"""

		guess = f'{proof},{lastProof}'.encode()
		guessHash = hashlib.sha256(guess).hexdigest()

		return guessHash[:4] == "0000"



	@property
	def lastBlock(self):
		"""
		the last block of the blockchain
		"""