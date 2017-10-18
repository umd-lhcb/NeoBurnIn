#!/usr/bin/env python
#
# Last Change: Wed Oct 18, 2017 at 10:29 AM -0400

import socketserver


class TCPHandler(socketserver.BaseRequestHandler):
    '''
    Instantiated once per connection. Handles communication between server and
    client.
    '''

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("Client ip: {}".format(self.client_address[0]))
        print(self.data)


class Server():
    def __init__(self, host, port, max_connection=5, log_dir='/var/log/bUrnIn'):
        server = socketserver.TCPServer((host, port), TCPHandler)
        self.server = server
