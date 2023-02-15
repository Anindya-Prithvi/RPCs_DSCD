import logging, grpc
import uuid
import time

import registry_server_pb2
import registry_server_pb2_grpc
import community_server_pb2
import community_server_pb2_grpc

OPTIONS = """Options:
    1. Get server list
    2. Subscribe to server
    3. Leave a server
    4. Get article
    5. Publish article
Enter your choice[1-5]: """


def get_articles(logger: logging.Logger, client_id: uuid.UUID):
    addr = input("Enter address of server [dom:port]: ")
    with grpc.insecure_channel(addr) as channel:
        stub = community_server_pb2_grpc.ClientManagementStub(channel)
        req = community_server_pb2.ArticleRequestFormat()
        req.client.id = str(client_id)
        req.article.article_type = community_server_pb2.Article.type.SPORTS
        req.article.author = input("Enter author name:")
        # convert time in string to int using time
        time_lim = time.strptime(input("Enter time [d m Y]:"), "%d %m %Y")
        req.article.time = int(time.mktime(time_lim))

        response = stub.GetArticles(req)
        logger.info(
            "RECEIVED ARTICLES:\n"
            +
             "\n".join(
                [f"[{community_server_pb2.Article.type.Name(i.article_type)}]\n{i.author} - {i.time}\n{i.content}\n\n" for i in response.articles]
            )
        )

def publish_article(logger: logging.Logger, client_id: uuid.UUID):
    addr = input("Enter address of server [dom:port]: ")
    with grpc.insecure_channel(addr) as channel:
        stub = community_server_pb2_grpc.ClientManagementStub(channel)
        req = community_server_pb2.ArticleRequestFormat()
        req.client.id = str(client_id)
        req.article.article_type = community_server_pb2.Article.type.SPORTS
        req.article.author = "John Doe"
        req.article.time = 14383294526
        req.article.content = "This is a test article"
        response = stub.PublishArticle(req)
        logger.info(f'{"SUCCESS" if response.value else "FAILURE"}')

def join_or_leave_Server(
    logger: logging.Logger, client_id: uuid.UUID, join: bool = True
):
    addr = input("Enter address of server [dom:port]: ")
    with grpc.insecure_channel(addr) as channel:
        stub = community_server_pb2_grpc.ClientManagementStub(channel)
        if join:
            response = stub.JoinServer(
                registry_server_pb2.Client_information(id=str(client_id))
            )
        else:
            response = stub.LeaveServer(
                registry_server_pb2.Client_information(id=str(client_id))
            )
        logger.info(f'{"SUCCESS" if response.value else "FAILURE"}')


def getServersfromRegistry(logger: logging.Logger, client_id: uuid.UUID):
    with grpc.insecure_channel("[::1]:21337") as channel:
        stub = registry_server_pb2_grpc.MaintainStub(channel)
        response = stub.GetServerList(
            registry_server_pb2.Client_information(id=str(client_id))
        )
        logger.info(
            "RECEIVED SERVER LIST:\n"
            + "\n".join([f"{i.name} - {i.addr}" for i in response.servers])
        )


def run(client_id: uuid.UUID, logger: logging.Logger):
    print("Starting client, EOF is EOP")
    while True:
        try:
            val = input(OPTIONS)
            if val == "1":
                getServersfromRegistry(logger, client_id)
            elif val == "2":
                join_or_leave_Server(logger, client_id, True)
            elif val == "3":
                join_or_leave_Server(logger, client_id, False)
            elif val == "4":
                get_articles(logger, client_id)
            elif val == "5":
                publish_article(logger, client_id)
            else:
                print("Invalid choice")
        except EOFError:
            print("EOF. Exiting")
            break
        except KeyboardInterrupt:
            print("Keyboard Interrupt. Exiting")
            break
        # generic exception
        except Exception as e:
            # print error with description and traceback
            logger.exception(e)


if __name__ == "__main__":
    logging.basicConfig()
    client_id = uuid.uuid1()
    logger = logging.getLogger(f"client-{client_id}")
    logger.setLevel(logging.INFO)
    logger.info("Client ID: %s", client_id)
    run(client_id, logger)
