import pika
import uuid
import sys
import registry_server_pb2
import community_server_pb2

CLIENTELE = community_server_pb2.Clientele()
MAXCLIENTS = 5
# ARTICLESLIST = community_server_pb2.ArticleList()
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()

def on_request_new(ch, method, props, body):
    request = registry_server_pb2.Client_information()
    request.ParseFromString(body)
    if (request.type == "join"):
        if (len(CLIENTELE.clients) >= MAXCLIENTS):
            client_info = registry_server_pb2.Success(value=False)
            client_info_bytes = client_info.SerializeToString()
            channel.basic_publish(exchange='', routing_key='client_server', body=client_info_bytes)
        elif (registry_server_pb2.Client_information(id=request.id) in CLIENTELE.clients):
            client_info = registry_server_pb2.Success(value=False)
            client_info_bytes = client_info.SerializeToString()
            channel.basic_publish(exchange='', routing_key='client_server', body=client_info_bytes)
        else:
            client_info = registry_server_pb2.Success(value=True)
            client_info_bytes = client_info.SerializeToString()
            CLIENTELE.clients.append(registry_server_pb2.Client_information(id=request.id))
            channel.basic_publish(exchange='', routing_key='client_server', body=client_info_bytes)
    elif (request.type == "leave"):
        if (registry_server_pb2.Client_information(id=request.id) in CLIENTELE.clients):
            CLIENTELE.clients.remove(registry_server_pb2.Client_information(id=request.id))
            client_info = registry_server_pb2.Success(value=True)
            client_info_bytes = client_info.SerializeToString()
            channel.basic_publish(exchange='', routing_key='client_server', body=client_info_bytes)
        else:
            client_info = registry_server_pb2.Success(value=False)
            client_info_bytes = client_info.SerializeToString()
            channel.basic_publish(exchange='', routing_key='client_server', body=client_info_bytes)
    for i in CLIENTELE.clients:
                print(i.id)



def on_request(ch, method, props, body):
    request = registry_server_pb2.Success()
    request.ParseFromString(body)
    if (request.value == True):
        print("SUCCESS\n")
    channel.stop_consuming()

def serve(name, port):
    client_info = registry_server_pb2.Server_information(type="register", name=str(name), addr=str(port))
    client_info_bytes = client_info.SerializeToString()
    channel.basic_publish(exchange='', routing_key='registry_server', body=client_info_bytes)
    channel.basic_consume(queue="first_server", on_message_callback=on_request)
    print("Server started, listening for requests")
    channel.start_consuming()
    channel.basic_consume(queue="first_server", on_message_callback=on_request_new)
    channel.start_consuming()

if __name__ == "__main__":
    channel.queue_delete(queue='first_server')
    channel.queue_declare(queue="first_server")
    if len(sys.argv) == 3:
        name = sys.argv[1]
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Port must be an integer")
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)
        serve(name, port)
        print("Here 2")
    else:
        print("Usage: python server.py <name> <port>")
        sys.exit(1)