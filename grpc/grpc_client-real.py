import logging, grpc
import uuid

import registry_server_pb2
import registry_server_pb2_grpc


def run(client_id: uuid.UUID, logger: logging.Logger):
    print("Will try to conquer the world ...")

    with grpc.insecure_channel("localhost:21337") as channel:
        stub = registry_server_pb2_grpc.MaintainStub(channel)
        response = stub.GetServerList(
            registry_server_pb2.Client_information(id=str(client_id))
        )
        logger.info(
            "Received server list:\n"
            + "\n".join([f"{i.name}-{i.addr}" for i in response.servers])
        )


if __name__ == "__main__":
    logging.basicConfig()
    client_id = uuid.uuid1()
    logger = logging.getLogger(f"client-{client_id}")
    logger.setLevel(logging.INFO)
    logger.info("Client ID: %s", client_id)
    run(client_id, logger)
