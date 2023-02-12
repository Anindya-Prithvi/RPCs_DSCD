from concurrent import futures
import logging

import grpc
import registry_server_pb2
import registry_server_pb2_grpc

logger = logging.getLogger()
logger.setLevel(logging.INFO)

registered = registry_server_pb2.Server_book()
server_lim = 5

class Maintain(registry_server_pb2_grpc.MaintainServicer):

    def RegisterServer(self, request, context):
        # TODO: name and addr should be unique
        new_server = registered.servers.add()
        new_server.name = "lol"
        new_server.addr = request.addr
        return registry_server_pb2.Success(value=True)

    def GetServerList(self, request, context):
        book_of_5 = registry_server_pb2.Server_book()
        book_of_5.servers.extend(registered.servers[:5])
        return book_of_5


def serve():
    port = '21337'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    registry_server_pb2_grpc.add_MaintainServicer_to_server(Maintain(), server)
    server.add_insecure_port('[::]:' + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
