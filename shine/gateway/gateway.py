# -*- coding: utf-8 -*-


import signal
import sys
import weakref
import uuid
import setproctitle

import gevent
from gevent.queue import Queue
import zmq.green as zmq  # for gevent

from .server import Server
from ..share.proc_mgr import ProcMgr
from ..share.log import logger
from ..share import constants, shine_pb2
from ..share.config import ConfigAttribute, Config


class Gateway(object):
    ############################## configurable begin ##############################

    name = ConfigAttribute('NAME')
    debug = ConfigAttribute('DEBUG')

    ############################## configurable end   ##############################

    config = None

    proc_mgr = None
    outer_server = None
    inner_server = None
    forwarder_client = None

    # 准备发送到worker的queue
    task_queue = None

    # worker唯一标示
    proc_id = None
    # 连接ID->conn
    conn_dict = None
    # 用户ID->conn
    user_dict = None

    # 存储存储userid->proc_id
    user_redis = None

    def __init__(self, box_class):
        self.config = Config(defaults=constants.DEFAULT_CONFIG)
        self.proc_mgr = ProcMgr()
        self.outer_server = Server(box_class, self.config['GATEWAY_BACKLOG'])
        self.task_queue = Queue()
        self.conn_dict = dict()
        self.user_dict = weakref.WeakValueDictionary()

    def run(self, debug=None):
        """
        启动
        :param debug: 是否debug
        :return:
        """

        if debug is not None:
            self.debug = debug

        if self.config['USER_REDIS_URL']:
            import redis
            self.user_redis = redis.from_url(self.config['USER_REDIS_URL'])

        workers = len(self.config['GATEWAY_INNER_ADDRESS_LIST'])

        def run_wrapper():
            logger.info('Running server, debug: %s, workers: %s',
                        self.debug, workers)

            self._prepare_server()
            setproctitle.setproctitle(self._make_proc_name('gateway:master'))
            # 只能在主线程里面设置signals
            self._handle_parent_proc_signals()
            self.proc_mgr.fork_workers(workers, self._worker_run)

        run_wrapper()

    def _make_proc_name(self, subtitle):
        """
        获取进程名称
        :param subtitle:
        :return:
        """
        proc_name = '[%s %s:%s] %s' % (
            self.name,
            constants.NAME,
            subtitle,
            ' '.join([sys.executable] + sys.argv)
        )

        return proc_name

    def _make_redis_key(self, uid):
        return self.config['USER_REDIS_KEY_TPL'] % uid

    def _prepare_server(self):
        """
        准备server，因为fork之后就晚了
        :return:
        """
        self.outer_server._prepare_server((self.config['GATEWAY_OUTER_HOST'], self.config['GATEWAY_OUTER_PORT']))

    def _serve_forever(self):
        """
        保持运行
        :return:
        """
        job_list = []
        for action in [self.outer_server._serve_forever, self._fetch_from_forwarder, self._send_task_to_worker]:
            job = gevent.spawn(action)
            job_list.append(job)

        for job in job_list:
            job.join()

    def _start_inner_server(self, address):
        """
        zmq的内部server
        每个worker绑定的地址都要不一样
        """
        ctx = zmq.Context()
        self.inner_server = ctx.socket(zmq.PUSH)
        self.inner_server.bind(address)

    def _fetch_from_forwarder(self):
        """
        从forwarder server那拿数据
        :return:
        """

        ctx = zmq.Context()
        self.forwarder_client = ctx.socket(zmq.SUB)
        for address in self.config['FORWARDER_OUTPUT_ADDRESS_LIST']:
            self.forwarder_client.connect(address)
        self.forwarder_client.setsockopt(zmq.SUBSCRIBE, self.proc_id)

        while True:
            topic, msg = self.forwarder_client.recv_multipart()

            task = shine_pb2.Task()
            task.ParseFromString(msg)

            logger.debug('task:\n%s', task)

            # 这样就不会内存泄露了
            job = gevent.spawn(self._handle_task, task)
            job.join()

    def _handle_task(self, task):
        """
        处理task
        :param task:
        :return:
        """

        if task.cmd == constants.CMD_WRITE_TO_CLIENT:
            conn = self.conn_dict.get(task.client_id)
            if conn:
                conn.write(task.data)
        elif task.cmd == constants.CMD_WRITE_TO_WORKER:
            # 重新转发处理
            # 标记一下
            task.inner = 1
            self.task_queue.put(task)
        elif task.cmd == constants.CMD_CLOSE_CLIENT:
            conn = self.conn_dict.get(task.client_id)
            if conn:
                conn.close()
        elif task.cmd == constants.CMD_LOGIN_CLIENT:
            conn = self.conn_dict.get(task.client_id)
            if conn:
                if conn.uid is not None:
                    # 旧的登录用户

                    # 先从存储删掉
                    if self.user_redis:
                        # TODO 要确定与worker_uuid相等才能删除
                        self.user_redis.delete(self._make_redis_key(conn.uid))

                    self.user_dict.pop(conn.uid, None)
                    conn.uid = conn.userdata = None

                conn.uid = task.uid
                conn.userdata = task.userdata
                self.user_dict[conn.uid] = conn

                # 后写入存储
                if self.user_redis:
                    self.user_redis.set(self._make_redis_key(conn.uid), self.proc_id, ex=self.config['USER_REDIS_MAXAGE'])

        elif task.cmd == constants.CMD_LOGOUT_CLIENT:
            conn = self.conn_dict.get(task.client_id)
            if conn:
                if conn.uid is not None:
                    if self.user_redis:
                        self.user_redis.delete(self._make_redis_key(conn.uid))

                    self.user_dict.pop(conn.uid, None)
                    conn.uid = conn.userdata = None

        elif task.cmd == constants.CMD_WRITE_TO_USERS:
            rsp = shine_pb2.RspToUsers()
            rsp.ParseFromString(task.data)

            for row in rsp.rows:
                for uid in row.uids:
                    conn = self.user_dict.get(uid)
                    if conn and (conn.userdata & row.userdata) == row.userdata:
                        conn.write(row.buf)

        elif task.cmd == constants.CMD_CLOSE_USERS:
            rsp = shine_pb2.CloseUsers()
            rsp.ParseFromString(task.data)

            for uid in rsp.uids:

                conn = self.user_dict.get(uid)
                if conn and (conn.userdata & rsp.userdata) == rsp.userdata:
                    conn.close()

    def _send_task_to_worker(self):
        """
        将任务发送到worker
        :return:
        """

        while True:
            task = self.task_queue.get()
            self.inner_server.send(task.SerializeToString())

    def _register_outer_server_handlers(self):
        """
        注册server的一些回调
        :return:
        """

        @self.outer_server.create_conn
        def create_conn(conn):
            logger.debug('conn.id: %r', conn.id)
            self.conn_dict[conn.id] = conn

            task = shine_pb2.Task()
            task.proc_id = self.proc_id
            task.client_id = conn.id
            task.client_ip = conn.address[0]
            task.cmd = constants.CMD_CLIENT_CREATED

            self.task_queue.put(task)

        @self.outer_server.close_conn
        def close_conn(conn):
            # 删除
            logger.debug('conn.id: %r', conn.id)
            self.conn_dict.pop(conn.id, None)
            if conn.uid is not None:
                if self.user_redis:
                    self.user_redis.delete(self._make_redis_key(conn.uid))

                self.user_dict.pop(conn.uid, None)
                conn.uid = conn.userdata = None

            task = shine_pb2.Task()
            task.proc_id = self.proc_id
            task.client_id = conn.id
            task.client_ip = conn.address[0]
            task.cmd = constants.CMD_CLIENT_CLOSED

            self.task_queue.put(task)

        @self.outer_server.handle_request
        def handle_request(conn, data):
            # 转发到worker
            logger.debug('conn.id: %r, data: %r', conn.id, data)
            task = shine_pb2.Task()
            task.proc_id = self.proc_id
            task.client_id = conn.id
            task.client_ip = conn.address[0]
            task.cmd = constants.CMD_CLIENT_REQ
            task.data = data
            self.task_queue.put(task)

    def _worker_run(self, index):
        """
        在worker里面执行的
        :return:
        """
        setproctitle.setproctitle(self._make_proc_name('gateway:app:%s' % index))
        self.proc_id = uuid.uuid4().bytes
        self._handle_child_proc_signals()
        self._register_outer_server_handlers()
        self._start_inner_server(self.config['GATEWAY_INNER_ADDRESS_LIST'][index])

        try:
            self._serve_forever()
        except KeyboardInterrupt:
            pass
        except:
            logger.error('exc occur.', exc_info=True)

    def _handle_parent_proc_signals(self):
        def exit_handler(signum, frame):
            self.proc_mgr.enable = False

            # 如果是终端直接CTRL-C，子进程自然会在父进程之后收到INT信号，不需要再写代码发送
            # 如果直接kill -INT $parent_pid，子进程不会自动收到INT
            # 所以这里可能会导致重复发送的问题，重复发送会导致一些子进程异常，所以在子进程内部有做重复处理判断。
            self.proc_mgr.terminate_all()

        # INT, QUIT, TERM为强制结束
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGQUIT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)

    def _handle_child_proc_signals(self):
        def exit_handler(signum, frame):
            # 防止重复处理KeyboardInterrupt，导致抛出异常
            if self.proc_mgr.enable:
                self.proc_mgr.enable = False
                raise KeyboardInterrupt

        # 强制结束，抛出异常终止程序进行
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGQUIT, exit_handler)
        signal.signal(signal.SIGTERM, exit_handler)