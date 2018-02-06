#!/usr/bin/env python
#
# Last Change: Mon Feb 05, 2018 at 06:38 PM -0500

import asyncio

from bUrnIn.framework.base import Server


class ServerAsync(Server):
    '''
    TCP server that handles all connections in a single process using asyncio.
    '''
    def __init__(self,
                 ip, port,
                 msg_queue, logger_name,
                 timeout=5, size=4096, max_retries=3):
        # Store all unterminated clients in a dictionary
        self.clients = dict()

        super(ServerAsync, self).__init__(ip, port, msg_queue, logger_name,
                                          timeout, size, max_retries)

    def start(self):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.client_accept, self.ip, self.port,
                                    loop=loop)
        server = loop.run_until_complete(coro)

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            self.logger.info("Shutdown signal received. Prepare TCP server shutdown.")
        finally:  # Exit gracefully
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()
            self.msg_queue.put(None)  # This tells the dispatcher to shutdown

    def client_accept(self, client_reader, client_writer):
        task = asyncio.ensure_future(
            self.client_handle(client_reader, client_writer))
        self.clients[task] = (client_reader, client_writer)

        def client_done(task):
            del self.clients[task]
            client_writer.close()

        task.add_done_callback(client_done)

    @asyncio.coroutine
    def client_handle(self, client_reader, client_writer):
        retries = 0

        # Here we design a very simple protocol:
        #   Messages can have variable length, but it's end is indicated by a
        #   'EOM' byte array.
        #   We require the receiving length should at least be 3.
        #   We also require the message be encoded in UTF-8.

        EOM = bytearray(b'EOM')
        msg = bytearray()

        while True:
            # Asynchronously read chunks of data from the socket
            try:
                chunk = yield from asyncio.wait_for(
                    client_reader.read(self.size), timeout=self.timeout)
                msg.extend(chunk)

            except asyncio.TimeoutError:
                # Keep trying until we reach the maximum retries
                retries += 1
                # Also, clear the full buffer and start from scratch
                msg.clear()

                if retries is self.max_retries:
                    self.logger.error("TimeoutError: Maximum retries exceeded.")
                    break

            except Exception as err:
                self.logger.error("%: Transmission failed"
                                  % err.__class__.__name__)
                break

            # NOTE: This clause is only executed when NO exception is raised
            else:
                # NOTE: We require the length of the message to be no less than
                # 3.
                if msg[-3:] == EOM:
                    self.msg_queue.put(bytes(msg[:-3]).decode("utf-8"))
                    # We reached 'EOM': End-Of-Message
                    break
