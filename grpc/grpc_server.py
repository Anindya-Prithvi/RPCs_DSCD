# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter server."""

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
        # print(request, context.__dict__)
        # logger.info(context.peer()); no need imo, there will be a seperate server running for server
        # help(context)
        
        # logger.info(request)
        
        new_server = registered.servers.add()
        new_server.name = "lol"
        new_server.addr = request.addr
        return registry_server_pb2.Success(value=True)

    def GetServerList(self, request, context):
        # print(request, context.__dict__)
        # logger.info(context.peer());
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
