from concurrent import futures
import logging

import sys
import grpc
import registry_server_pb2
import registry_server_pb2_grpc

logger = logging.getLogger("registrar")
logger.setLevel(logging.INFO)
MAXSERVERS = 5 #default, changeable by command line arg

registered = registry_server_pb2.Server_book()


class Maintain(registry_server_pb2_grpc.MaintainServicer):
    def RegisterServer(self, request, context):
        logger.info(
            "JOIN REQUEST FROM %s",
            context.peer(),
        )
        if len(registered.servers) >= MAXSERVERS:
            return registry_server_pb2.Success(value=False)
        if any(
            i.name == request.name or i.addr == request.addr for i in registered.servers
        ):
            return registry_server_pb2.Success(value=False)
        new_server = registered.servers.add()
        new_server.name = request.name
        new_server.addr = request.addr
        return registry_server_pb2.Success(value=True)

    def GetServerList(self, request, context):
        logger.info(
            "SERVER LIST REQUEST FROM %s with id %s",
            context.peer(),
            request.id,
        )
        return registered


def serve():
    port = "21337"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    registry_server_pb2_grpc.add_MaintainServicer_to_server(Maintain(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    # get sys args
    
    if len(sys.argv) > 1:
        try:
            MAXSERVERS = int(sys.argv[1])
        except ValueError:
            print("Invalid number of servers")
            print("Usage: python registry_server.py [number of servers]")
            sys.exit(1)
    logging.basicConfig()
    serve()
