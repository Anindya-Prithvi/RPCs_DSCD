import sys, logging
import grpc
from concurrent import futures

import registry_server_pb2
import registry_server_pb2_grpc

logger = logging.getLogger("server")
logger.setLevel(logging.INFO)

def register_server(name, addr):
    with grpc.insecure_channel('localhost:21337') as channel:
        stub = registry_server_pb2_grpc.MaintainStub(channel)
        response = stub.RegisterServer(registry_server_pb2.Server_information(name=name, addr=addr))
        return response.value

def serve(name: str, port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # TODO: Add servicer for publishing and subscribing
    # registry_server_pb2_grpc.add_MaintainServicer_to_server(Maintain(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    logger.info("Server started, listening on " + str(port))
    if register_server(name, "[::]:" + str(port)):
        logger.info("Server registered")
    else:
        logger.error("Server registration failed. Fatal error.")
        exit(1)
    
    # server.wait_for_termination()
    logger.info("Server is running. \n1. Subscribe to another server\n2. Ctrl+C to stop server")
    while True:
        try:
            choice = int(input())
            if choice == 1:
                pass
        except ValueError:
            logger.info("Invalid choice")
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt. Stopping server")
            break
    server.stop(0)

if __name__ == '__main__':
    #accept command line args name and port
    logging.basicConfig()
    if len(sys.argv) == 3:
        name = sys.argv[1]
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Port must be an integer")
            sys.exit(1)
        if port<1024 or port>65535:
            print("Port must be between 1024 and 65535")
            sys.exit(1)
        logger.info("Starting server %s on port %d", name, port)
        serve(name, port)
    else:
        print("Usage: python community_server.py <name> <port>")
        sys.exit(1)

