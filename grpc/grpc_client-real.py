import logging, grpc
import uuid

import registry_server_pb2
import registry_server_pb2_grpc

OPTIONS = """Options:
    1. Get server list
    2. Subscribe to server
    3. Publish an article
    4. Get article
Enter your choice[1-4]: """

def getServersfromRegistry(logger: logging.Logger, client_id: uuid.UUID):
    with grpc.insecure_channel("[::1]:21337") as channel:
        stub = registry_server_pb2_grpc.MaintainStub(channel)
        response = stub.GetServerList(
            registry_server_pb2.Client_information(id=str(client_id))
        )
        logger.info(
            "Received server list:\n"
            + "\n".join([f"{i.name}-{i.addr}" for i in response.servers])
        )

def run(client_id: uuid.UUID, logger: logging.Logger):
    print("Starting client, EOF is EOP")
    while True:
        try:
            val = input(OPTIONS)
            if val == "1":
                getServersfromRegistry(logger, client_id)
            else:
                print("Invalid choice")
        except EOFError:
            print("EOF. Exiting")
            break
        except KeyboardInterrupt:
            print("Keyboard Interrupt. Exiting")
            break

if __name__ == "__main__":
    logging.basicConfig()
    client_id = uuid.uuid1()
    logger = logging.getLogger(f"client-{client_id}")
    logger.setLevel(logging.INFO)
    logger.info("Client ID: %s", client_id)
    run(client_id, logger)
