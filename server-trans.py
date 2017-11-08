#!/usr/bin/env python
#
# Last Change: Wed Nov 08, 2017 at 11:17 AM -0500

from configparser import ConfigParser
from os import getcwd
from os.path import join, isfile

from bUrnIn.server.transmission import TransmissionServer
from bUrnIn.output.sqlite import sql_write


def parse_config(cfg):
    config = ConfigParser()
    opts_dict = dict()

    config.read(cfg)

    for key in config:
        opts_dict[key] = config[key]

    return opts_dict


class Server(TransmissionServer):
    def dispatcher(self, msg, address, err=None):
        msg = msg[:-1]  # Remove trailing '\n' characater

        # We require '|' to be the delimiter
        msg_bundle = msg.split('|')
        msg_bundle = msg_bundle[:-1]  # Remove trailing ''

        # The first two entries are headers
        header = msg_bundle[:2]
        hostname = header[0]
        timestamp = header[1]

        # # The rest are all data
        data_bundle = msg_bundle[2:]
        data = dict()
        for i in range(0, int(len(data_bundle)/2)):
            data[data_bundle[2*i]] = float(data_bundle[2*i + 1])

        sql_write(self.db_filename, hostname, timestamp, data)


if __name__ == "__main__":
    GLOBAL_CFG  = '/etc/server-trans/config'
    DEFAULT_CFG = join(getcwd(), 'server-trans.cfg')

    if isfile(GLOBAL_CFG):
        opts = parse_config('/etc/server-trans/config')
    else:
        opts = parse_config(join(getcwd(), 'server-trans.cfg'))

    server = Server(opts['main']['ip'], int(opts['main']['port']),
                    size=int(opts['main']['size']),
                    max_retries=int(opts['main']['max_retries']),
                    max_connections=int(opts['main']['max_connections']),
                    timeout=int(opts['main']['timeout']),
                    db_filename=opts['db']['filename'],
                    log_filename=opts['log']['filename']
                    )

    server.listen()
