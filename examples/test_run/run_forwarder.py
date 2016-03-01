# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()

import sys
sys.path.insert(0, '../../')

from zmq_server import Forwarder
import constants


forwarder = Forwarder()

if __name__ == '__main__':
    forwarder.run(
        constants.RESULTER_PULL_ADDRESS_LIST,
        constants.RESULTER_PUB_ADDRESS_LIST,
        'redis://127.0.0.1:6379/0',
        'zmq:user:%s',
    )