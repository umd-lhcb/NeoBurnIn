#!/usr/bin/env python3
#
# Last Change: Wed Jul 22, 2020 at 02:57 AM +0800

from rpi.burnin.USBRelay import set_relay_state, get_all_device_paths, OFF


def turn_off_usb_relay(num_of_chs=2):
    print('Turning OFF all USB relays...')
    for relay in get_all_device_paths():
        print('Turning OFF channels of relay {}'.format(relay.decode('utf-8')))
        for ch in range(num_of_chs):
            set_relay_state(relay, ch, OFF)
            print('Channel {} is set to OFF.'.format(ch))
