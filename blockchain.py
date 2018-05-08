import hashlib
import json
import requests

from textwrap import dedent
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse


class Blockchain(object):

	def __init__(self):
		self.chain = []
		self.currentTransactions = []

		# Create the first block
		self.newBlock(previousHash=1, proof=100)

		# Set of nodes on the network
		self.nodes = set()


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

		while self.validProof(proof, lastProof) == False:
			proof += 1

		return proof


	def registerNode(self, address):
		"""
		Add a new node to the list of nodes

		:param address:		<str>	Address of a node Eg: "http//192.168.0.5:5000"
		:return: 			None 
		"""

		parsedURL = urlparse(address)
		self.nodes.add(parsedURL.netloc)


	def validChain(self, chain):
		"""
		Determine if blockchain is valid or not

		:param chain:	<list> a blockchain
		:return:		<Bool> true iff valid
		"""

		lastBlock = chain[0]
		curreentIndex = 1

		while curreentIndex < len(chain):

			block = chain[curreentIndex]
			print(f'{lastBlock}')
			print(f'{block}')
			print("\n---------------\n")

			# check if the block's hash is correct
			if block['previousHash'] != self.hash(lastBlock):
				return False

			# check proof of work is correct
			if not self.validProof(lastBlock['proof'], block['proof']):
				return False

			lastBlock = block
			curreentIndex += 1

		return True


	def resolveConflicts(self):
		"""
		This is the consensus algorithm
		Replaces the chain with the longest existing chain in the network

		:return:	<Bool>	True iff chain was replaced 
		"""

		neighbours = self.nodes
		newChain = None

		maxLen = len(self.chain)

		# Grab and verify chain from all the nodes in the network
		for node in neighbours:
			response = requests.get(f'http://{node}/chain')

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']

				#check if the length is longer and valid
				if length > maxLen and self.validChain(chain):
					maxLen = length
					newChain = chain

		# Replace our chain if we discovered a new, valid chain longer than ours
		if newChain:
			self.chain = newChain
			return True

		return False 


	@property
	def lastBlock(self):
		"""
		the last block of the blockchain
		"""
		return self.chain[-1]


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


	@staticmethod
	def hash(block):
		"""
		Creates a SHA256 hash of a block

		:param block:	<dict>	a Block
		:return:		<str> SHA256 of the block
		"""

		blockStr = json.dumps(block, sort_keys=True).encode()

		return hashlib.sha256(blockStr).hexdigest()


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
nodeIdentifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route("/mine", methods=["GET"])
def mine():

	# Run proof of work algorithm to get next proof
	lastBlock = blockchain.lastBlock
	lastProof = lastBlock['proof']
	proof = blockchain.proofOfWork(lastProof)

	# Must recieve reward for mining
	blockchain.newTransaction(
		sender="0",
		recipient= nodeIdentifier,
		amount=1,
	)

	#Forge the new Block by adding it to the blockchain
	previousHash = blockchain.hash(lastBlock)
	block = blockchain.newBlock(proof, previousHash)

	response = {
		'message': "New Block forged",
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'previousHash': block['previousHash'],
	}

	return jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def newTransaction():

	values = request.get_json()
	## print(values)
	# extract and check for required fields
	required = ['sender', 'recipient', 'amount']
	if not all(k in values for k in required):
		return 'Missing Values', 400

	# Create a new transaction
	index = blockchain.newTransaction(values['sender'], values['recipient'], values['amount'])
	response = ('message', f'Transaction will be added to block {index}')

	return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def fullChain():

	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}

	return jsonify(response), 200


@app.route("/nodes/register", methods=["POST"])
def registerNodes():
	values = request.get_json()

	nodes = values.get('nodes')
	if nodes is None:
		return "Error: Please supply a valid list of nodes", 400

	for node in nodes:
		blockchain.registerNode(node)

	response = {
		'message': 'New nodes have been added',
		'total_nodes': list(blockchain.nodes),
	}
	return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolveConflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == "__main__":
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
	args = parser.parse_args()
	port = args.port

	app.run(host='0.0.0.0', port=port)