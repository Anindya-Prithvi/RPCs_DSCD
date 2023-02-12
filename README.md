# Repository for DSCD Assignments
## Assignment 1: RPCs
In this assignment we had to implement a Discord like platform, i.e. a registry server which contains all communities, each community having channels. 

Flow:  
1. Registry server goes live at globally known location.
2. Server `s1` goes live too but isn't known, so, `s1` sends a request to registry server and the registry server stores their name and location (ip:port)
3. Now any client who wants to read articles from a server first has to request their names and locations from the registry. After that, they may join those servers and request articles.

We implemented the above with RPCs, protocol buffers. [gRPC, RabbitMQ, ZeroMQ]
