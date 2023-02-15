import pika
import uuid
import registry_server_pb2
import community_server_pb2

registered = registry_server_pb2.Server_book()

def registerserver(name, port):
    if name in [i.name for i in registered.servers]:
        print("Server name already registered")
        return registry_server_pb2.Success(value=False)
    new_server = registered.servers.add()
    new_server.name = name
    new_server.addr = f"localhost:{port}"
    return registry_server_pb2.Success(value=True)

def on_request(ch, method, props, body):
    request = registry_server_pb2.Server_information()
    request.ParseFromString(body)
    print("Received request from client {}".format(request.name))
    if (request.type == "register"):
        response = registerserver(request.name, request.addr)

def serve():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.queue_delete(queue='registry_server')
    channel.queue_declare(queue="registry_server")
    channel.basic_consume(queue="registry_server", on_message_callback=on_request)
    print("Server started, listening for requests")
    channel.start_consuming()

if __name__ == "__main__":
    serve()