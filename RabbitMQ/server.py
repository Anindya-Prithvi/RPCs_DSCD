import pika
import uuid
import sys
import registry_server_pb2
import community_server_pb2

def serve(name, port):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    client_info = registry_server_pb2.Server_information(type=str("register"), name=str(name), addr=str(port))
    client_info_bytes = client_info.SerializeToString()
    channel.basic_publish(exchange='', routing_key='registry_server', body=client_info_bytes)
    print('Sent join request for client {}'.format(name))

if __name__ == "__main__":
    if len(sys.argv) == 3:
        name = sys.argv[1]
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Port must be an integer")
            sys.exit(1)
        serve(name, port)
    else:
        print("Usage: python server.py <name> <port>")
        sys.exit(1)