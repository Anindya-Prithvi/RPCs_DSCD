import logging, grpc
import uuid

import registry_server_pb2
import registry_server_pb2_grpc
logger = logging.getLogger("client")
logger.setLevel(logging.INFO)

def run(client_id: uuid.UUID):
    print("Will try to conquer the world ...")

    with grpc.insecure_channel('localhost:21337') as channel:
        stub = registry_server_pb2_grpc.MaintainStub(channel)
        response = stub.GetServerList(registry_server_pb2.Client_information(id=str(client_id)))
        logger.info(response.servers)


if __name__ == '__main__':
    logging.basicConfig()
    logger.info(run)
    client_id = uuid.uuid4()
    logger.info("Client ID: %s", client_id)
    run(client_id)
