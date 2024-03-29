import sys, logging
import grpc
import time
from concurrent import futures

import registry_server_pb2
import registry_server_pb2_grpc
import community_server_pb2
import community_server_pb2_grpc
import bonus_pb2
import bonus_pb2_grpc

CLIENTELE = community_server_pb2.Clientele()
SERVERELE = bonus_pb2.Serverele()
ARTICLESLIST = community_server_pb2.ArticleList()
MAXCLIENTS = 5

def join_server_from_server(name: str, port:int):
    addr = input("Enter address of server [dom:port]: ")
    with grpc.insecure_channel(addr) as channel:
        stub = bonus_pb2_grpc.ServerServerManagementStub(channel)
        response = stub.JoinServer(
            registry_server_pb2.Server_information(name=name, addr = "[::1]:"+str(port))
        )
        logger.info("REMOTE ARTICLES DUMPED")
        for i in response.articles:
            if i not in ARTICLESLIST.articles:
                ARTICLESLIST.articles.append(i)
                # TODO: dump
                for j in SERVERELE.servers:
                    with grpc.insecure_channel(j.addr) as channel2:
                        stub = bonus_pb2_grpc.ServerServerManagementStub(channel2)
                        response = stub.DumpArticles(i)
                        logger.info("DUMPED TO CHILD")

def leave_server_from_server(name: str, port: int):
    addr = input("Enter address of server [dom:port]: ")
    with grpc.insecure_channel(addr) as channel:
        stub = bonus_pb2_grpc.ServerServerManagementStub(channel)
        response = stub.LeaveServer(
            registry_server_pb2.Server_information(name=name, addr = "[::1]:"+str(port))
        )
        logger.info(f"RECEIVED STATUS: {response}")

class ClientManagement(community_server_pb2_grpc.ClientManagementServicer):
    def JoinServer(self, request, context):
        logger.info(f"JOIN REQUEST FROM {request.id}")
        # Check if server is full
        if len(CLIENTELE.clients) >= MAXCLIENTS:
            return registry_server_pb2.Success(value=False)
        # Assumption duplicacy of client rejected
        if registry_server_pb2.Client_information(id=request.id) in CLIENTELE.clients:
            return registry_server_pb2.Success(value=False)
        # Add client to server
        CLIENTELE.clients.append(registry_server_pb2.Client_information(id=request.id))
        return registry_server_pb2.Success(value=True)

    def LeaveServer(self, request, context):
        logger.info(f"LEAVE REQUEST FROM {request.id}")
        if registry_server_pb2.Client_information(id=request.id) in CLIENTELE.clients:
            CLIENTELE.clients.remove(
                registry_server_pb2.Client_information(id=request.id)
            )
            return registry_server_pb2.Success(value=True)
        # cannot leave if not joined
        return registry_server_pb2.Success(value=False)

    def GetArticles(self, request, context):
        # Remember clients are stateless
        logger.info(f"ARTICLE REQUEST FROM {request.client.id}")
        if (
            registry_server_pb2.Client_information(id=request.client.id)
            in CLIENTELE.clients
        ):

            responselist = []
            for i in ARTICLESLIST.articles:
                if (not request.article.HasField("article_type")) or (
                    request.article.article_type == i.article_type
                ):
                    pass
                else:
                    continue
                if request.article.author == i.author or request.article.author == "":
                    pass
                else:
                    continue
                if request.article.time < i.time:
                    pass
                else:
                    continue
                responselist.append(i)
            return community_server_pb2.ArticleList(articles=responselist)
        else:
            # abort request if not joined
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Not joined")

    def PublishArticle(self, request, context):
        # Remember clients are stateless
        logger.info(f"ARTICLE PUBLISH REQUEST FROM {request.client.id}")
        if (
            registry_server_pb2.Client_information(id=request.client.id)
            in CLIENTELE.clients
        ):
            type_article = request.article.article_type
            author_article = request.article.author
            time_article = request.article.time
            content_article = request.article.content

            if time_article != 0:
                logger.error("Time is present")
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Time is present")

            article_new = community_server_pb2.Article()
            # check if article_type is present in oneof
            if not request.article.HasField("article_type"):
                logger.error("Article type not present")
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, "Article type not present"
                )
                return
            # if length of content exceeds 200 chars, reject
            if len(content_article) > 200:
                logger.error("Content length exceeds 200 chars")
                context.abort(
                    grpc.StatusCode.INVALID_ARGUMENT, "Content length exceeds 200 chars"
                )
                return
            article_new.article_type = type_article
            article_new.author = author_article
            # get current time in seconds since epoch
            article_new.time = int(time.time())
            article_new.content = content_article
            ARTICLESLIST.articles.append(article_new)
            for j in SERVERELE.servers:
                with grpc.insecure_channel(j.addr) as channel2:
                    stub = bonus_pb2_grpc.ServerServerManagementStub(channel2)
                    response = stub.DumpArticles(article_new)
                    logger.info("DUMPED TO CHILD")
            return registry_server_pb2.Success(value=True)
        else:
            # abort request if not joined
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Not joined")


class ServerServerManagement(bonus_pb2_grpc.ServerServerManagementServicer):
    def JoinServer(self, request, context):
        logger.info(f"JOIN REQUEST FROM {request.name}-{request.addr}")
        # Assumption duplicacy of server rejected
        if (
            registry_server_pb2.Server_information(name=request.name, addr=request.addr)
            in SERVERELE.servers
        ):
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Rejoined")
            return
        # Add server (client) to server
        SERVERELE.servers.append(
            registry_server_pb2.Server_information(name=request.name, addr=request.addr)
        )
        return ARTICLESLIST
    
    def LeaveServer(self, request, context):
        logger.info(f"LEAVE REQUEST FROM {request.name}-{request.addr}")
        if (
            registry_server_pb2.Server_information(name=request.name, addr=request.addr)
            in SERVERELE.servers
        ):
            return registry_server_pb2.Success(value=True)
        # cannot leave if not joined
        return registry_server_pb2.Success(value=False)
    
    def DumpArticles(self, request, context):
        logger.info(f"NEW ARTICLE DUMP") # kinda insecure but idc
        if request not in ARTICLESLIST.articles:
            for j in SERVERELE.servers:
                with grpc.insecure_channel(j.addr) as channel2:
                    stub = bonus_pb2_grpc.ServerServerManagementStub(channel2)
                    response = stub.DumpArticles(request)
                    logger.info("DUMPED TO CHILD")
            ARTICLESLIST.articles.append(request)
            return registry_server_pb2.Success(value=True)
        # cannot dump if not joined
        return registry_server_pb2.Success(value=False)
        


def register_server(name, addr):
    with grpc.insecure_channel("[::1]:21337") as channel:
        stub = registry_server_pb2_grpc.MaintainStub(channel)
        response = stub.RegisterServer(
            registry_server_pb2.Server_information(name=name, addr=addr)
        )
        logger.info(f'Received status: {"SUCCESS" if response.value else "FAILURE"}')
        return response.value


def serve(name: str, port: int, logger: logging.Logger):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # TODO: Add servicer for publishing and subscribing
    community_server_pb2_grpc.add_ClientManagementServicer_to_server(
        ClientManagement(), server
    )
    bonus_pb2_grpc.add_ServerServerManagementServicer_to_server(
        ServerServerManagement(), server
    )
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    logger.info("Server started, listening on " + str(port))
    if register_server(name, "[::1]:" + str(port)):
        logger.info("Server registered")
    else:
        logger.error("Server registration failed. Fatal error.")
        exit(1)

    # server.wait_for_termination()
    logger.info(
        "Server is running. \n1. Subscribe to another server\n2. Leave server\n Ctrl+C to stop server"
    )
    while True:
        try:
            choice = int(input())
            if choice == 1:
                join_server_from_server(name, port)
            elif choice==2:
                leave_server_from_server(name, port)
            else:
                print("Invalid choice")
        except ValueError:
            logger.info("Invalid choice")
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt. Stopping server")
            break
        except EOFError:
            logger.warning("Running in non interactive mode")
            server.wait_for_termination()
        except Exception as e:
            # print error with description and traceback
            logger.exception(e)
    server.stop(0)


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
        serve(name, port, logger)
    else:
        print("Usage: python community_server.py <name> <port>")
        sys.exit(1)
