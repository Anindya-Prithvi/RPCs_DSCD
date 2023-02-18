import pika
import uuid
import time
import datetime
import community_server_pb2
import registry_server_pb2

connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
channel = connection.channel()

OPTIONS = """Options:
    1. Get server list
    2. Subscribe to server
    3. Leave a server
    4. Get article
    5. Publish article
Enter your choice[1-5]: """

def just_print_it(ch, method, properties, body):
    request = registry_server_pb2.Success()
    request.ParseFromString(body)
    if (request.value == True):
        print("SUCCESS\n")
    else:
        print("FAILURE\n")
    channel.stop_consuming()

def article_list(ch, method, properties, body):
    request = community_server_pb2.ArticleList()
    request.ParseFromString(body)
    if (request.success == True):
        print("Article List:")
        for article in request.articles:
            print("Article Type: {}".format(article.article_type))
            print("Author: {}".format(article.author))
            print("Time: {}".format(article.time))
            print("Content: {}".format(article.content))
            print("")
        channel.stop_consuming()
    else:
        print("FAILURE\n")
        channel.stop_consuming()

def fetch_article(client_id, port):
    try:
        request = community_server_pb2.ArticleRequestFormat()
        request.client.id = str(client_id)
        request.type = "fetch"
        try:
            request.article.article_type = getattr(community_server_pb2.Article.type, input("Type of article [SPORTS, FASHION, POLITICS]: "),)
        except:
            print("Invalid article type")
        author_name = input("Enter author's name: ")
        if (len(author_name) == 0):
            print("Author's name cannot be empty")
        else :
            request.article.author = author_name
        try:
            date_entry = input('Enter a date in YYYY-MM-DD format: ')
            year, month, day = map(int, date_entry.split('-'))
            date1 = datetime.date(year, month, day)
            request.article.time = date1.strftime("%Y-%m-%d")
        except:
            print("Invalid time format, using current time")
            request.article.time = datetime.datetime.now().strftime("%Y-%m-%d")
        client_info = request  
        client_info_bytes = client_info.SerializeToString()
        channel.basic_publish(exchange='', routing_key='first_server', body=client_info_bytes)
        print('Sent article request for client {}'.format(client_id))
        channel.basic_consume(queue='client_server', on_message_callback=article_list)
        channel.start_consuming()
    except Exception as e:
        print("Error in fetching article")

def publish_article(client_id, port):
    try:
        request = community_server_pb2.ArticleRequestFormat()
        request.client.id = str(client_id)
        request.type = "publish"
        try:
            request.article.article_type = getattr(community_server_pb2.Article.type, input("Type of article [SPORTS, FASHION, POLITICS]: "),)
        except:
            print("Invalid article type")
            return
        request.article.author = input("Enter author's name: ")
        if (len(request.article.author) == 0):
            print("Author's name cannot be empty")
            return
        request.article.content = input("Content of the article[<= 200 char]: ")
        client_info = request
        client_info_bytes = client_info.SerializeToString()
        channel.basic_publish(exchange='', routing_key='first_server', body=client_info_bytes)
        print('Sent article request for client {}'.format(client_id))
        channel.basic_consume(queue='client_server', on_message_callback=just_print_it)
        channel.start_consuming()
    except Exception as e:
        print("Error in publishing article2")
    


def join_or_leave_server(client_id, port, join=True):
    # dom = input("Enter domain of server: ")
    # port = input("Enter port of server: ")
    if join:
        # channel.queue_declare(queue='join_queue', exclusive=True)
        client_info = registry_server_pb2.Client_information(id=str(client_id), type="join")
        client_info_bytes = client_info.SerializeToString()
        channel.basic_publish(exchange='', routing_key='first_server', body=client_info_bytes)
        print('Sent join request for client {}'.format(client_id))
        channel.basic_consume(queue='client_server', on_message_callback=just_print_it)
        channel.start_consuming()
    else:
        # channel.queue_declare(queue='leave_queue', exclusive=True)
        client_info = registry_server_pb2.Client_information(id=str(client_id), type="leave")
        client_info_bytes = client_info.SerializeToString()
        channel.basic_publish(exchange='', routing_key='first_server', body=client_info_bytes)
        print('Sent leave request for client {}'.format(client_id))
        channel.basic_consume(queue='client_server', on_message_callback=just_print_it)
        channel.start_consuming()


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
                join_or_leave_server(client_id, port, False)
            elif val == "4":
                fetch_article(client_id, port)
            elif val == "5":
                publish_article(client_id, port)
            else:
                print("Invalid choice")
        except EOFError:
            break
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    client_id = uuid.uuid1()
    begin_operation(client_id, "8000")