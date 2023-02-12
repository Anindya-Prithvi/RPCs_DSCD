import logging

import grpc
import registry_server_pb2
import registry_server_pb2_grpc


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    print("Will try to greet world ...")
    with grpc.insecure_channel("localhost:21337") as channel:
        stub = registry_server_pb2_grpc.MaintainStub(channel)
        response = stub.RegisterServer(
            registry_server_pb2.Server_information(
                name="Bankai", addr=str(__import__("time").time())
            )
        )
        print("Grpc client [as a server] received: 1 " + str(response))
    with grpc.insecure_channel("localhost:21337") as channel:
        stub = registry_server_pb2_grpc.MaintainStub(channel)
        response = stub.GetServerList(
            registry_server_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        )
        print("Grpc client [as a server] received: 2 " + str(response.servers))


if __name__ == "__main__":
    logging.basicConfig()
    my_logger = logging.getLogger(__name__)
    my_logger.setLevel(logging.INFO)
    my_logger.info(run)
    run()
