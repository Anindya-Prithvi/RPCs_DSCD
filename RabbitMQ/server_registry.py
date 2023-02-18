import pika
import uuid
import registry_server_pb2
import community_server_pb2

host = "localhost"
port = 12001

registered = registry_server_pb2.Server_book()
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
channel = connection.channel()

def registerserver(name, port):
    if name in [i.name for i in registered.servers]:
        print("Server name already registered")
        return registry_server_pb2.Success(value=False)
    print("Join request from {} at port {}".format(name, port))
    new_server = registered.servers.add()
    new_server.name = name
    new_server.addr = f"localhost:{port}"
    return registry_server_pb2.Success(value=True)

def on_request(ch, method, props, body):
    request = registry_server_pb2.Server_information()
    request.ParseFromString(body)
    if (request.type == "register"):
        response = registerserver(request.name, request.addr)
        if (response.value == True):
            client_info = registry_server_pb2.Success(value=True)
            client_info_bytes = client_info.SerializeToString()
            channel.basic_publish(exchange='', routing_key=str(request.name), body=client_info_bytes)
    request2 = registry_server_pb2.Client_information()
    request2.ParseFromString(body)
    if (request2.type == "get"):
        client_info = registered
        client_info_bytes = client_info.SerializeToString()
        channel.basic_publish(exchange='', routing_key=str(request2.id), body=client_info_bytes)
        print("Sent server list to client {}".format(request.name))

def serve():
    channel.queue_delete(queue='registry_server')
    channel.queue_declare(queue="registry_server")
    channel.basic_consume(queue="registry_server", on_message_callback=on_request)
    print("Server started, listening for requests")
    channel.start_consuming()

if __name__ == "__main__":
    serve()