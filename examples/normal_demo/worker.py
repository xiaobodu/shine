# -*- coding: utf-8 -*-


import sys
sys.path.insert(0, '../../')

import time
from shine import Worker, logger


app = Worker()


@app.create_client
def create_client(request):
    logger.debug(request)


@app.close_client
def close_client(request):
    logger.debug(request)


@app.route(1)
def reg(request):
    request.write_to_client(dict(
        ret=0,
    ))


@app.route(2)
def login(request):
    logger.error("login: %s", request)
    uid = request.box.get_json()["uid"]
    if uid == 1:
        request.login_client(uid, 1)
    elif uid == 2:
        request.login_client(uid, 2)
    elif uid == 3:
        request.login_client(uid)
    else:
        # 不登录
        request.write_to_client(dict(
            ret=100,
        ))
        return
        
    # time.sleep(40)
    # request.logout_client()
    request.write_to_client(dict(
        ret=0,
        body="login %s" % uid
    ))


@app.route(3)
def handle_users(request):
    jdata = request.box.get_json()

    uids = jdata['uids']
    userdata = jdata['userdata']
    exclude = jdata['exclude']
    op_type = jdata['op_type']

    if op_type == 'write':
        request.write_to_users([
            (uids, dict(cmd=1, body='from request: %s' % int(time.time())), userdata, exclude)
        ])
    else:
        request.close_users(uids, userdata, exclude)


@app.route(4)
def close_users(request):
    request.close_users([1, 2])
    request.write_to_client(dict(
        ret=100,
        body='ok'
    ))


@app.route(5)
def handle_trigger(request):
    logger.error('from trigger.write_to_worker, task:\n%s', request.task)
