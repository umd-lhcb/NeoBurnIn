#!/usr/bin/env python
#
# Last Change: Mon Feb 05, 2018 at 06:21 PM -0500

from datetime import datetime

from bUrnIn.framework.base import Dispatcher
from bUrnIn.framework.base import standard_time_format


class DispatcherServer(Dispatcher):
    '''
    Dispatch received data. This Dispatcher runs in a separated process.
    '''
    def __init__(self, msg_queue, logger_name, datalogger_name):
        # For email anti-flooding
        self.last_sent_timestamp = None

        super(DispatcherServer, self).__init__(
            msg_queue, logger_name, datalogger_name)

    def filter(self, data):
        self.logger.info(data)
        # for entry in data:
            # try:
                # # We require '|' to be the delimiter inside an entry
                # date, ch_name, value = entry.split('|')[:-1]
            # except Exception as err:
                # self.log.error("{}: Corrupted data: {}.".format(
                    # err.__class__.__name__, entry))
                # break

            # # Make sure the datetime is valid
            # try:
                # # timestamp = datetime.strptime(
                    # # date, standard_time_format).timestamp()
                # datetime.strptime(date, standard_time_format)
            # except Exception as err:
                # self.log.error("{}: Corrupted date entry: {}.".format(
                    # err.__class__.__name__, date
                # ))
                # break

            # try:
                # value = float(value)

                # if value >= self.hardware_failure:
                    # warning = "WARNING: A hardware failure is detected: The {} reads a voltage of {}".format(
                        # ch_name, value
                    # )
                    # self.log.error(warning)
                    # self.email_antiflood(warning)
            # except Exception as err:
                # self.log.error("{}: Corrupted value entry: {}.".format(
                    # err.__class__.__name__, value
                # ))
                # break

            # try:
                # self.datalog.info('{}, {}, {}'.format(
                    # date, ch_name, value))
            # except Exception as err:
                # self.log.error("{}: Cannot write to CSV file.".format(
                    # err.__class__.__name__
                # ))
                # break
        # self.log.debug('Message processing finished...')

    def email_antiflood(self, warning):
        pass
        # if self.last_sent_timestamp is None:
            # # We never sent any email before
            # self.log.critical(warning)
            # self.last_sent_timestamp = datetime.now()

        # else:
            # # If we have sent emails recently, don't send any email again
            # # This is to prevent email flooding
            # delta_t = \
                # (datetime.now() - self.last_sent_timestamp).total_seconds() / 60
            # self.log.debug(delta_t)

            # if delta_t >= self.log_email_interval:
                # self.log.critical(warning)
                # # Update the timestamp, only if we sent a new email.
                # self.last_sent_timestamp = datetime.now()
            # else:
                # pass