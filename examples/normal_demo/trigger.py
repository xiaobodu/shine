# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '../../')
import time
from shine import Trigger
from shine.share import constants

import config


def send_data(trigger):

    # uids = [constants.CONNS_AUTHED]
    uids = [constants.CONNS_ALL]
    # uids = [constants.CONNS_UNAUTHED]

    userdata = 0
    # userdata = 1

    # exclude = None
    exclude = [1]

    print trigger.write_to_users([
        (uids, dict(cmd=1, body='direct event from trigger: %s' % int(time.time())), userdata, exclude)
    ])

    # print trigger.close_users(uids, userdata, exclude)

    # op_type = 'write'
    op_type = 'close'

    # print trigger.write_to_worker(dict(
    #     cmd=3,
    #     ret=100,
    #     body=json.dumps(dict(
    #         uids=uids,
    #         userdata=userdata,
    #         exclude=exclude,
    #         op_type=op_type,
    #     )),
    # ))


def main():
    trigger = Trigger(forwarder_input_address_list=config.FORWARDER_INPUT_ADDRESS_LIST)

    for it in xrange(0, 99999):
        time.sleep(1)

        send_data(trigger)


if __name__ == '__main__':
    main()
