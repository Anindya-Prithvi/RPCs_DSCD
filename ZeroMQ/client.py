import logging
import datetime
import zmq
import uuid
import community_server_pb2
import registry_server_pb2


OPTIONS = """Options:
    1. Get server list
    2. Subscribe to server
    3. Leave a server
    4. Get article
    5. Publish article
Enter your choice[1-5]: """


def article_list(body):
    request = community_server_pb2.ArticleList()
    request.ParseFromString(body)
    dict = {1: "SPORTS", 2: "FASHION", 3: "POLITICS"}
    if (request.success == True):
        print("Article List:")
        for i, article in enumerate(request.articles):
            val = dict[article.article_type + 1]
            print("{}. Article Type: ".format(i + 1))
            print(val)
            # print(type(article.article_type))
            print("Author: {}".format(article.author))
            print("Time: {}".format(article.time))
            print("Content: {}".format(article.content))
            print("\n")
    else:
        logger.info("No articles found")
        print("FAILURE\n")
        return


def get_articles(logger: logging.Logger, client_id: uuid.UUID):
    ctx = zmq.Context()
    socket = ctx.socket(zmq.REQ)
    addr = input("Enter address of server [tcp://host:port]: ")
    socket.connect(f'tcp://127.0.0.1:'+addr)
    try:
        req = community_server_pb2.ArticleRequestFormat()
        req.client.id = str(client_id)
        req.type = "fetch"
        try:
            req.article.article_type = getattr(
                community_server_pb2.Article.type, input("Type of article [SPORTS, FASHION, POLITICS]: ")
            )
        except:
            logger.warning("Invalid article type, defaulting to UNSPECIFIED")
        author_name = input("Enter author name:")
        if len(author_name) == 0:
            logger.warning("Author name is empty, defaulting to UNSPECIFIED")
        else:
            req.article.author = author_name
        # convert time in string to int using time
        try:
            date_entry = input('Enter a date in YYYY-MM-DD format: ')
            year, month, day = map(int, date_entry.split('-'))
            date1 = datetime.date(year, month, day)
            req.article.time = date1.strftime("%Y-%m-%d")
        except:
            print("Invalid time format, using current time")
            req.article.time = datetime.datetime.now().strftime("%Y-%m-%d")

        socket.send(req.SerializeToString())
        resp_data = socket.recv()
        response = community_server_pb2.ArticleList()
        article_list(resp_data)

    except Exception as e:
        logger.error(f"FAIL: {e}")
    finally:
        socket.close()
        ctx.term()
        
def publish_article(logger: logging.Logger, client_id: uuid.UUID):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    addr = input("Enter address of server [ip:port]: ")
    socket.connect(f'tcp://127.0.0.1:'+addr)

    req = community_server_pb2.ArticleRequestFormat()
    req.client.id = str(client_id)
    req.type = "publish"
    try:
        req.article.article_type = getattr(
            community_server_pb2.Article.type,
            input("Type of article [SPORTS, FASHION, POLITICS]: "),
        )
    except:
        logger.error("Invalid article type")
        return
    req.article.author = input("Author of article: ")
    if len(req.article.author) == 0:
        logger.error("Author name cannot be empty")
        return
    req.article.content = input("Content of the article[<=200 char]: ")

    # Send the request and wait for a response
    socket.send(req.SerializeToString())
    response_bytes = socket.recv()
    response = registry_server_pb2.Success()
    response.ParseFromString(response_bytes)

    logger.info(f'{"SUCCESS" if response.value else "FAILURE"}')

    
def join_or_leave_Server(logger: logging.Logger, client_id: uuid.UUID, join: bool = True):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    addr = input("Enter address of server [ip:port]: ")
    # print(type(addr))
    socket.connect(f'tcp://127.0.0.1:'+addr)
    req = registry_server_pb2.Client_information()
    req.id = str(client_id)
    req.type = "join" if join else "leave"

    # Send the request and wait for a response
    socket.send(req.SerializeToString())
    response_bytes = socket.recv()
    # print(response_bytes)
    response = registry_server_pb2.Success()
    response.ParseFromString(response_bytes)

    logger.info(f'{"SUCCESS" if response.value else "FAILURE"}')
    

def getServersfromRegistry(logger: logging.Logger, client_id: uuid.UUID):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    # connect to port 21337
    socket.connect("tcp://localhost:21337")

    request = registry_server_pb2.Client_information(id=str(client_id))
    socket.send(request.SerializeToString())
    response_bytes = socket.recv()
    response = registry_server_pb2.Server_book.FromString(response_bytes)
    logger.info("RECEIVED SERVER LIST:\n" + "\n".join([f"{i.name} - {i.addr}" for i in response.servers]))

def run(client_id: uuid.UUID, logger: logging.Logger):
    print("Starting client, EOF is EOP; Servers listen on *all* ip")
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
