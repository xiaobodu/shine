# -*- coding: utf-8 -*-

from ..share.log import logger
from ..share import constants
from ..share.shine_pb2 import RspToUsers, CloseUsers, Task
from ..trigger.trigger import Trigger


class Request(object):
    """
    请求
    """

    # 与gateway的连接对象
    conn = None
    # gateway封装的task
    task = None
    # 业务box
    box = None
    # 数据是否有效
    is_valid = False
    # 是否已经作出回应
    responded = False
    blueprint = None
    # 路由表
    route_rule = None
    # 是否中断处理，即不调用view_func，主要用在before_request中
    interrupted = False

    trigger = None

    def __init__(self, conn, task):
        self.conn = conn
        self.task = task
        # 赋值
        self.is_valid = self._parse_raw_data()
        self.trigger = Trigger(self.app.box_class, zmq_client=self.app.forwarder_client)

    @property
    def app(self):
        return self.conn.app

    def _parse_raw_data(self):
        if not self.task.body:
            return True

        try:
            self.box = self.app.box_class()
        except Exception, e:
            logger.error('parse raw_data fail. e: %s, request: %s', e, self)
            return False

        if self.box.unpack(self.task.body) > 0:
            self._parse_route_rule()
            return True
        else:
            logger.error('unpack fail. request: %s', self)
            return False

    def _parse_route_rule(self):
        if self.cmd is None:
            return

        route_rule = self.app.get_route_rule(self.cmd)
        if route_rule:
            # 在app层，直接返回
            self.route_rule = route_rule
            return

        for bp in self.app.blueprints:
            route_rule = bp.get_route_rule(self.cmd)
            if route_rule:
                self.blueprint = bp
                self.route_rule = route_rule
                break

    @property
    def cmd(self):
        try:
            return self.box.cmd
        except:
            return None

    @property
    def view_func(self):
        return self.route_rule['view_func'] if self.route_rule else None

    @property
    def endpoint(self):
        if not self.route_rule:
            return None

        bp_endpoint = self.route_rule['endpoint']

        return '.'.join([self.blueprint.name, bp_endpoint] if self.blueprint else [bp_endpoint])

    def write_to_client(self, data):
        """
        写回
        :param data: 可以是dict也可以是box
        :return:
        """

        assert not (self.app.rsp_once and self.responded), 'request has been responded'

        if isinstance(data, self.app.box_class):
            data = data.pack()
        elif isinstance(data, dict):
            data = self.box.map(data).pack()

        task = Task()
        # 就可以直接通过node_id和client_id来进行识别了
        task.client_id = self.task.client_id
        task.node_id = self.task.node_id
        task.cmd = constants.CMD_WRITE_TO_CLIENT
        task.body = data

        succ = self.conn.write(task.SerializeToString())

        if succ:
            # 如果发送成功，就标记为已经回应
            self.responded = True

        return succ

    def close_client(self):
        task = Task()
        task.client_id = self.task.client_id
        task.node_id = self.task.node_id
        task.cmd = constants.CMD_CLOSE_CLIENT

        return self.conn.write(task.SerializeToString())

    def login_client(self, uid, userdata=None):

        task = Task()
        task.client_id = self.task.client_id
        task.node_id = self.task.node_id
        task.cmd = constants.CMD_LOGIN_CLIENT
        task.uid = uid
        task.userdata = userdata or 0

        return self.conn.write(task.SerializeToString())

    def logout_client(self):
        task = Task()
        task.client_id = self.task.client_id
        task.node_id = self.task.node_id
        task.cmd = constants.CMD_LOGOUT_CLIENT

        return self.conn.write(task.SerializeToString())

    def write_to_users(self, data_list):
        """
        格式为
        [(uids, box), (uids, box, userdata) ...]
        :param data_list: userdata可不传，默认为0，conn.userdata & userdata == userdata
        :return:
        """

        return self.trigger.write_to_users(data_list)

    def close_users(self, uids, userdata=None):
        return self.trigger.close_users(uids, userdata)

    def write_to_worker(self, data):
        """
        透传到worker进行处理
        """

        return self.trigger.write_to_worker(data, node_id=self.task.node_id)

    def interrupt(self, data=None):
        """
        中断处理
        :param data: 要响应的数据，不传即不响应
        :return:
        """
        self.interrupted = True
        if data is not None:
            return self.write_to_client(data)
        else:
            return True

    def __repr__(self):
        return 'cmd: %r, endpoint: %s, task:\n%s' % (self.cmd, self.endpoint, self.task)
