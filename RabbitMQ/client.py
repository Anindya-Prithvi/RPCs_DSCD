import pika
import uuid
import community_server_pb2
import registry_server_pb2

connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
channel = connection.channel()

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

def handle_server_list_response(ch, method, properties, body):
    server_list = registry_server_pb2.Server_book()
    print(server_list)
    server_list.ParseFromString(body)
    for i in server_list.servers:
        print(i.name, i.addr + "\n")
    channel.stop_consuming()

def get_server_list(client_id, port):
    client_info = registry_server_pb2.Client_information(id=str(client_id), type="get")
    client_info_bytes = client_info.SerializeToString()
    channel.basic_publish(exchange='', routing_key='registry_server', body=client_info_bytes)
    print('Sent get server list request for client {}'.format(client_id))
    channel.basic_consume(queue='client_server', on_message_callback=handle_server_list_response)
    channel.start_consuming()

def begin_operation(client_id, port):
    print("From client.py")
    channel.queue_delete(queue='client_server')
    channel.queue_declare(queue='client_server')
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