import pika
import uuid
import sys
import time
import datetime
import registry_server_pb2
import community_server_pb2

CLIENTELE = community_server_pb2.Clientele()
MAXCLIENTS = 5
ARTICLESLIST = community_server_pb2.ArticleList()
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", heartbeat=1800))
channel = connection.channel()

def on_request_new(ch, method, props, body):
    request = registry_server_pb2.Client_information()
    request.ParseFromString(body)
    if (request.type == "join"):
        if (len(CLIENTELE.clients) >= MAXCLIENTS):
            client_info = registry_server_pb2.Success(value=False)
            client_info_bytes = client_info.SerializeToString()
            print("Max clients reached")
            channel.basic_publish(exchange='', routing_key=str(request.id), body=client_info_bytes)
        elif (registry_server_pb2.Client_information(id=request.id) in CLIENTELE.clients):
            client_info = registry_server_pb2.Success(value=False)
            client_info_bytes = client_info.SerializeToString()
            print("Client already registered")
            channel.basic_publish(exchange='', routing_key=str(request.id), body=client_info_bytes)
        else:
            client_info = registry_server_pb2.Success(value=True)
            client_info_bytes = client_info.SerializeToString()
            print("Join request from {}".format(request.id))
            CLIENTELE.clients.append(registry_server_pb2.Client_information(id=request.id))
            channel.basic_publish(exchange='', routing_key=str(request.id), body=client_info_bytes)
    
    elif (request.type == "leave"):
        if (registry_server_pb2.Client_information(id=request.id) in CLIENTELE.clients):
            CLIENTELE.clients.remove(registry_server_pb2.Client_information(id=request.id))
            client_info = registry_server_pb2.Success(value=True)
            client_info_bytes = client_info.SerializeToString()
            print("Leave request from {}".format(request.id))
            channel.basic_publish(exchange='', routing_key=str(request.id), body=client_info_bytes)
        else:
            client_info = registry_server_pb2.Success(value=False)
            client_info_bytes = client_info.SerializeToString()
            channel.basic_publish(exchange='', routing_key=str(request.id), body=client_info_bytes)
    
    else:
        request_server = community_server_pb2.ArticleRequestFormat()
        request_server.ParseFromString(body)
        if (request_server.type == "publish"):
            if (registry_server_pb2.Client_information(id=request_server.client.id) in CLIENTELE.clients):
                type_article = request_server.article.article_type
                author_article = request_server.article.author
                time_article = request_server.article.time
                content_article = request_server.article.content

                article_new = community_server_pb2.Article()
                if not request_server.article.HasField("article_type"):
                    return
                if len(content_article) > 200:
                    return
                article_new.article_type = type_article
                article_new.author = author_article
                # article_new.time = int(time.time())
                article_new.time = datetime.datetime.now().strftime("%Y-%m-%d")
                article_new.content = content_article
                ARTICLESLIST.articles.append(article_new)
                client_info = registry_server_pb2.Success(value=True)
                client_info_bytes = client_info.SerializeToString()
                channel.basic_publish(exchange='', routing_key=str(request_server.client.id), body=client_info_bytes)
                print("Article Publish from client: " + request_server.client.id) 
            else:
                client_info = registry_server_pb2.Success(value=False)
                client_info_bytes = client_info.SerializeToString()
                channel.basic_publish(exchange='', routing_key=str(request_server.client.id), body=client_info_bytes)
        
        elif (request_server.type == "fetch"):
            print("Article request from client: " + request_server.client.id)
            responses = []
            if (registry_server_pb2.Client_information(id=request_server.client.id) in CLIENTELE.clients):
                for i in ARTICLESLIST.articles:
                    if (not request_server.article.HasField("article_type") or (request_server.article.article_type == i.article_type)):
                        pass
                    else:
                        continue
                    if (request_server.article.author == i.author or request_server.article.author == ""):
                        pass
                    else:
                        continue
                    if request_server.article.time < i.time:
                        pass
                    else:
                        continue
                    responses.append(i)
                if len(responses) == 0:
                    client_info = community_server_pb2.ArticleList(articles=responses, success=False)
                    client_info_bytes = client_info.SerializeToString()
                    channel.basic_publish(exchange='', routing_key=str(request_server.client.id), body=client_info_bytes)
                else:
                    client_info = community_server_pb2.ArticleList(articles=responses, success=True)
                    client_info_bytes = client_info.SerializeToString()
                    channel.basic_publish(exchange='', routing_key=str(request_server.client.id), body=client_info_bytes)
            else:
                client_info = community_server_pb2.ArticleList(articles=responses, success=False)
                client_info_bytes = client_info.SerializeToString()
                channel.basic_publish(exchange='', routing_key=str(request_server.client.id), body=client_info_bytes) 


def on_request(ch, method, props, body):
    request = registry_server_pb2.Success()
    request.ParseFromString(body)
    if (request.value == True):
        print("SUCCESS\n")
    channel.stop_consuming()

def serve(name, port):
    while True:
        try:
            option = int(input("Enter 1 to register\n"))
            if (option == 1):
                client_info = registry_server_pb2.Server_information(type="register", name=str(name), addr=str(port))
                client_info_bytes = client_info.SerializeToString()
                channel.basic_publish(exchange='', routing_key='registry_server', body=client_info_bytes)
                channel.basic_consume(queue=str(name), on_message_callback=on_request)
                print("Server started, listening for requests")
                channel.start_consuming()
                channel.basic_consume(queue=str(name), on_message_callback=on_request_new)
                channel.start_consuming()
        except KeyboardInterrupt:
            channel.queue_delete(queue=str(name))
            break

            

if __name__ == "__main__":
    if len(sys.argv) == 3:
        name = sys.argv[1]
        channel.queue_declare(queue=str(name))
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Port must be an integer")
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
        serve(name, port)
    else:
        print("Usage: python server.py <name> <port>")
        sys.exit(1)