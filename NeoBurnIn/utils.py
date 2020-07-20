#!/usr/bin/env python3
#
# Last Change: Tue Jul 21, 2020 at 12:07 AM +0800

from rpi.burnin.USBRelay import set_relay_state, get_all_device_paths


def turn_on_usb_relay(num_of_chs=2):
    print('Turning on all USB relays...')
    for relay in get_all_device_paths():
        print('Turning on channels of relay {}'.format(relay.decode('utf-8')))
        for ch in range(num_of_chs):
            set_relay_state(relay, ch)
            print('Channel {} is set to ON.'.format(ch))
