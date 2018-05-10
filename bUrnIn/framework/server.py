#!/usr/bin/env python
#
# Last Change: Tue May 08, 2018 at 04:29 PM -0400

import asyncio

from bUrnIn.framework.base import Server


class ServerAsync(Server):
    EOM = bytearray(b'EOM')

    '''
    TCP server that handles all connections in a single process using asyncio.
    '''
    def run(self, wait_event=None):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(self.client_handle, self.ip, self.port,
                                    loop=loop)
        server = loop.run_until_complete(coro)

        if wait_event is not None:
            wait_event.set()

        try:
            self.logger.info("Starting TCP server.")
            loop.run_forever()
        except KeyboardInterrupt:
            self.logger.info("Shutdown signal received. Prepare TCP server shutdown.")
        except Exception as err:
            self.logger.error("%s: Error received." % err.__class__.__name__)

        finally:  # Exit gracefully
            server.close()
            loop.run_until_complete(server.wait_closed())
            for task in asyncio.Task.all_tasks():
                task.cancel()
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()
            self.msg_queue.put(None)  # This tells the dispatcher to shutdown

    async def client_handle(self, client_reader, client_writer):
        retries = 0
        msg = bytearray()

        while not client_reader.at_eof():
            # Asynchronously read chunks of data from the socket.
            # We only read a chunk at a time, instead of trying to read the full
            # stream, to make sure that the timeout is not reached on normal
            # long stream transmission.
            try:
                chunk = await asyncio.wait_for(
                    client_reader.read(self.size), timeout=self.timeout)

            except asyncio.CancelledError:
                break

            except Exception as err:
                # Keep trying until we reach the maximum retries
                retries += 1
                self.logger.warning("%s: Failed to receive: %s time(s)."
                                    % (err.__class__.__name__, retries))
                # Also, clear the full buffer and start from scratch
                msg.clear()

                if retries is self.max_retries:
                    self.logger.error("%s: Maximum retries exceeded. Transmission failed."
                                      % err.__class__.__name__)
                    break

            # NOTE: This clause is only executed when NO exception is raised
            else:
                msg.extend(chunk)
                # NOTE: We require the length of the message to be no less than
                # 3.
                if msg[-3:] == self.EOM:
                    try:
                        self.msg_queue.put(msg[:-3].decode("utf-8"))
                        # We reached 'EOM': End-Of-Message
                    except Exception as err:
                        self.logger.error("%s: Cannot decode message."
                                          % err.__class__.__name__)
                    break

        # Always close the client socket in the end
        client_writer.close()
