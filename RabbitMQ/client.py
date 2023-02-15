import pika
import uuid
import community_server_pb2
import registry_server_pb2

OPTIONS = """Options:
    1. Get server list
    2. Subscribe to server
    3. Leave a server
    4. Get article
Enter your choice[1-4]: """

def join_or_leave_server(client_id, port, join=True):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
    channel = connection.channel()

    if join:
        channel.queue_declare(queue='join_queue', exclusive=True)
        client_info = registry_server_pb2.Client_information(id=str(client_id))
        client_info_bytes = client_info.SerializeToString()
        channel.basic_publish(exchange='', routing_key='join_queue', body=client_info_bytes)
        print('Sent join request for client {}'.format(client_id))
    else:
        channel.queue_declare(queue='leave_queue', exclusive=True)
        client_info = registry_server_pb2.Client_information(id=str(client_id))
        client_info_bytes = client_info.SerializeToString()
        channel.basic_publish(exchange='', routing_key='leave_queue', body=client_info_bytes)
        print('Sent leave request for client {}'.format(client_id))

    connection.close()

def get_server_list(client_id, port):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
    channel = connection.channel()

    # channel.queue_declare(queue='registry_server', exclusive=True)
    client_info = registry_server_pb2.Client_information(id=str(client_id))
    client_info_bytes = client_info.SerializeToString()
    channel.basic_publish(exchange='', routing_key='registry_server', body=client_info_bytes)
    print('Sent get server list request for client {}'.format(client_id))

    channel.basic_consume(queue='registry_server', on_message_callback=handle_server_list_response, auto_ack=True)

    connection.close()

def handle_server_list_response(ch, method, properties, body):
    server_list = registry_server_pb2.Server_book()
    server_list.ParseFromString(body)
    print('Received server list:\n' + '\n'.join([f"{i.name}-{i.addr}" for i in server_list.servers]))

def begin_operation(client_id, port):
    print("From client.py")
    while True:
        try:
            val = input(OPTIONS)
            if val == "1":
                get_server_list(client_id, port)
            elif val == "2":
                join_or_leave_server(client_id, port)
            elif val == "3":
                join_or_leave_server(client_id, port)
            else:
                print("Invalid choice")
        except EOFError:
            break
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    client_id = uuid.uuid1()
    begin_operation(client_id, "8000")