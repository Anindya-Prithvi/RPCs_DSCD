import sys, logging
import datetime
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
        if(registry_server_pb2.Client_information(id=article.client.id) in CLIENTELE.clients):
            type_article = article.article.article_type
            author_article = article.article.author
            time_article = article.article.time
            content_article = article.article.content

            article_new = community_server_pb2.Article()
            if not article.article.HasField("article_type"):
                return False
            if len(content_article) > 200:
                return False
            article_new.article_type = type_article
            article_new.author = author_article
            # article_new.time = int(time.time())
            article_new.time = datetime.datetime.now().strftime("%Y-%m-%d")
            article_new.content = content_article
            ARTICLESLIST.articles.append(article_new)
            client_info = registry_server_pb2.Success(value=True)
            client_info_bytes = client_info.SerializeToString()
            return True
        
        else:
            return False


    def get_articles(self,article):
        if(registry_server_pb2.Client_information(id=article.client.id) in CLIENTELE.clients):
            responses = []
            if (registry_server_pb2.Client_information(id=article.client.id) in CLIENTELE.clients):
                for i in ARTICLESLIST.articles:
                    if (not article.article.HasField("article_type") or (article.article.article_type == i.article_type)):
                        pass
                    else:
                        continue
                    if (article.article.author == i.author or article.article.author == ""):
                        pass
                    else:
                        continue
                    if article.article.time < i.time:
                        pass
                    else:
                        continue
                    responses.append(i)
            
            if(len(responses) == 0):
                return [False,[]]
            return [True,responses]

        else:
            return [False,[]]


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
                        logger.info("JOIN REQUEST FROM {}".format(client_id))
                        # send a success message
                        response = registry_server_pb2.Success(value= True)
                        # response.status = "SUCCESS"
                        socket.send(response.SerializeToString())
                    else:
                        logger.info("JOIN REQUEST FROM {}".format(client_id))
                        # send a failure message
                        response = registry_server_pb2.Success(value= False)
                        # response.status = "FAILURE"
                        socket.send(response.SerializeToString())
                
                elif (drresponse.type == "leave"):
                    client_id = drresponse.id
                    # leave the client
                    client_management = ClientManagement()
                    if client_management.leave(client_id):
                        logger.info("LEAVE REQUEST FROM {}".format(client_id))
                        # send a success message
                        response = registry_server_pb2.Success(value= True)
                        # response.status = "SUCCESS"
                        socket.send(response.SerializeToString())
                    else:
                        logger.info("LEAVE REQUEST FROM {}".format(client_id))
                        # send a failure message
                        response = registry_server_pb2.Success(value= False)
                        # response.status = "FAILURE"
                        socket.send(response.SerializeToString())

                else:
                    request_server = community_server_pb2.ArticleRequestFormat()
                    request_server.ParseFromString(response)
                    if (request_server.type == "publish"):
                        # publish the article
                        article_management = ArticleManagement()
                        if article_management.publish(request_server):
                            logger.info("ARTICLES PUBLISH FROM {}".format(request_server.client.id))
                            # send a success message
                            response = registry_server_pb2.Success(value= True)
                            # response.status = "SUCCESS"
                            socket.send(response.SerializeToString())
                        else:
                            logger.info("ARTICLES PUBLISH FROM {}".format(request_server.client.id))
                            # send a failure message
                            response = registry_server_pb2.Success(value= False)
                            # response.status = "FAILURE"
                            socket.send(response.SerializeToString())

                    elif (request_server.type == "fetch"):   
                        # fetch the article
                        article_management = ArticleManagement()
                        res = article_management.get_articles(request_server)
                        if res[0]:
                            logger.info("ARTICLES REQUEST FROM {}".format(request_server.client.id))
                            # send a success message
                            response = community_server_pb2.ArticleList(articles=article_management.get_articles(request_server)[1],success=1)
                            # response.status = "SUCCESS"
                            socket.send(response.SerializeToString())
                        else:
                            logger.info("ARTICLES REQUEST FROM {}".format(request_server.client.id))
                            # send a failure message
                            response = community_server_pb2.ArticleList(success=0)
                            # response.status = "FAILURE"
                            socket.send(response.SerializeToString())

                # logger.info("Received request: %s", response)
        
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
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        try:
            socket.bind(f"tcp://*:{port}")
        except zmq.error.ZMQError as e:
            print("Port already in use")
            sys.exit(1)
        logger.info("Starting server %s on port %d", name, port)
        if register_server(name, "[::1]:" + str(port)):
            logger.info("Server registered")
        else:
            logger.info("Server registration failed")
            sys.exit(1)
        serve(name, port, logger)
    else:
        print("Usage: python community_server.py <name> <port>")
        sys.exit(1)