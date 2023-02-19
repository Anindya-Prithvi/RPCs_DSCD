import sys, logging
import time
import zmq
from concurrent import futures

import registry_server_pb2
import community_server_pb2

logger = logging.getLogger("registrar")
logger.setLevel(logging.INFO)
MAXCLIENTS = 5  # default, changeable by command line arg

CLIENTELE = community_server_pb2.Clientele()
ARTICLESLIST = community_server_pb2.ArticleList()

class ClientManagement():
    def join(self, client_id):
        if (registry_server_pb2.Client_information(id=client_id) in CLIENTELE.clients) or (len(CLIENTELE.clients) >= MAXCLIENTS):
            return False
        elif len(CLIENTELE.clients) < MAXCLIENTS:
            CLIENTELE.clients.append(registry_server_pb2.Client_information(id=client_id))
            return True
        else:
            return False
    
    def leave(self, client_id):
        if registry_server_pb2.Client_information(id=client_id) in CLIENTELE.clients:
            CLIENTELE.clients.remove(registry_server_pb2.Client_information(id=client_id))
            return True
        else:
            return False
    
    def get_clientele(self):
        return CLIENTELE

class ArticleManagement():

    def publish(self, article):
        ARTICLESLIST.articles.append(article)
        return True

    def get_articles(self):
        return ARTICLESLIST



def register_server(name, addr):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:21337")

    # Send the server information as a message
    message = f"register {name} {addr}"
    print(f"Sending {message}")
    socket.send_string(message)

    # Wait for the response from the registry server
    response = socket.recv_string()

    # Check the response status and return True if successful, False otherwise
    success = response == "SUCCESS"
    logger.info(f"Received status: {'SUCCESS' if success else 'FAILURE'}")
    return success

def serve(name: str, port: int, logger: logging.Logger):
    while True:
        try:
            # context = zmq.Context()
            # socket = context.socket(zmq.REP)
            # socket.bind(f"tcp://*:{port}")
            # logger.info("Registry server started on port %s", port)
                # if register_server(name, "[::1]:" + str(port)):
                #     logger.info("Server registered")
                response = socket.recv()
                # deserialize the response
                drresponse = registry_server_pb2.Client_information()
                drresponse.ParseFromString(response)
                if (drresponse.type == "join"):
                    client_id = drresponse.id
                    # join the client
                    client_management = ClientManagement()
                    if client_management.join(client_id):
                        logger.info("Client joined")
                        # send a success message
                        response = registry_server_pb2.Success(value= True)
                        # response.status = "SUCCESS"
                        socket.send(response.SerializeToString())
                    else:
                        logger.info("Client not joined")
                        # send a failure message
                        response = registry_server_pb2.Success(value= False)
                        # response.status = "FAILURE"
                        socket.send(response.SerializeToString())
                
                elif (drresponse.type == "leave"):
                    client_id = drresponse.id
                    # leave the client
                    client_management = ClientManagement()
                    if client_management.leave(client_id):
                        logger.info("Client left")
                        # send a success message
                        response = registry_server_pb2.Success(value= True)
                        # response.status = "SUCCESS"
                        socket.send(response.SerializeToString())
                    else:
                        logger.info("Client not left")
                        # send a failure message
                        response = registry_server_pb2.Success(value= False)
                        # response.status = "FAILURE"
                        socket.send(response.SerializeToString())

                logger.info("Received request: %s", response)
        
        except KeyboardInterrupt as e:
            logger.info("Shutting down server")
            break

if __name__ == "__main__":
    # accept command line args name and port
    logging.basicConfig()
    if len(sys.argv) == 3:
        name = sys.argv[1]
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Port must be an integer")
            sys.exit(1)
        if port < 1024 or port > 65535:
            print("Port must be between 1024 and 65535")
            sys.exit(1)
        logger = logging.getLogger(f"{name}-{port}")
        logger.setLevel(logging.INFO)
        logger.info("Starting server %s on port %d", name, port)
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{port}")
        if register_server(name, "[::1]:" + str(port)):
            logger.info("Server registered")
        serve(name, port, logger)
    else:
        print("Usage: python community_server.py <name> <port>")
        sys.exit(1)