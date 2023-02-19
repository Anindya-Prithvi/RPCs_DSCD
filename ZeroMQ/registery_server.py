import logging
import zmq
import sys

import registry_server_pb2

logger = logging.getLogger("registrar")
logger.setLevel(logging.INFO)
MAXSERVERS = 5  # default, changeable by command line arg

registered = registry_server_pb2.Server_book()

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:21337")

class Maintain:
	def RegisterServer(self, name, addr):
		logger.info(
			"JOIN REQUEST FROM %s",
			addr,
		)
		if len(registered.servers) >= MAXSERVERS:
			return False
		if any(i.name == name or i.addr == addr for i in registered.servers):
			return False
		new_server = registered.servers.add()
		new_server.name = name
		new_server.addr = addr
		return True

	def GetServerList(self,id):
		return registered
    

if __name__ == "__main__":
    # get sys args

	if len(sys.argv) > 1:
		try:
			MAXSERVERS = int(sys.argv[1])
		except ValueError:
			print("Invalid number of servers")
			print("Usage: python registry_server.py [number of servers]")
			sys.exit(1)
	logging.basicConfig()
	port = "21337"
	context = zmq.Context()
	socket = context.socket(zmq.REP)
	socket.bind(f"tcp://*:{port}")
	logger.info("Registry server started on port %s", port)
	maintain = Maintain()
	while True:
		#  Wait for next request from client
		message = socket.recv()
		logger.info("Received request: %s", message)
		# check the length of the message
		if len(message.split()) != 3:
			val = maintain.GetServerList(message)
			# return the server list 
			socket.send(val.SerializeToString())
		else:
			# find name and ip of server
			name = message.split()[1]
			addr = message.split()[2][6:]
			if maintain.RegisterServer(name, addr):
				socket.send_string("SUCCESS")
			else:
				socket.send_string("FAILURE")
