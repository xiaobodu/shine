# -*- coding: utf-8 -*-


import signal
import sys
import weakref
import uuid
import setproctitle

import gevent
from gevent.queue import Queue
import zmq.green as zmq  # for gevent

from ..share.proc_mgr import ProcMgr
from ..share.log import logger
from ..share import constants, gw_pb2


class Resulter(object):
    name = constants.NAME
    debug = False

    proc_mgr = None
    zmq_pull_server = None
    zmq_pub_client = None

    # 准备发送到worker的queue
    task_queue = None

    outer_host = None
    outer_port = None
    inner_address = None
    result_address = None

    # worker唯一标示
    worker_uuid = None
    # 连接ID->conn
    conn_dict = None
    # 用户ID->conn
    user_dict = None

    def __init__(self, box_class):
        self.proc_mgr = ProcMgr()
        self.outer_server = Server(box_class)
        self.task_queue = Queue()

    def run(self, outer_host, outer_port, inner_address, result_address, debug=None, workers=None):
        """
        启动
        :param outer_host: 外部地址 '0.0.0.0'
        :param outer_port: 外部地址 7100
        :param inner_address: 内部地址 tcp://127.0.0.1:8833
        :param result_address: 结果地址 tcp://127.0.0.1:8855
        :param debug: 是否debug
        :param workers: 进程数
        :return:
        """

        self.outer_host = outer_host
        self.outer_port = outer_port
        self.inner_address = inner_address
        self.result_address = result_address
        self.conn_dict = dict()
        self.user_dict = weakref.WeakValueDictionary()

        if debug is not None:
            self.debug = debug

        workers = 1 if workers is None else workers

        def run_wrapper():
            logger.info('Running outer_host: %s, outer_port: %s, inner_address_list: %s, result_address_list: %s, debug: %s, workers: %s',
                        outer_host, outer_port,
                        inner_address,
                        result_address,
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

    def _prepare_server(self):
        """
        准备server，因为fork之后就晚了
        :return:
        """
        # zmq的内部server，要在worker fork之前就准备好
        ctx = zmq.Context()
        self.zmq_pull_server = ctx.socket(zmq.PUSH)
        self.zmq_pull_server.bind(self.inner_address)

        self.outer_server._prepare_server((self.outer_host, self.outer_port))

        self._register_server_handlers()

    def _serve_forever(self):
        """
        保持运行
        :return:
        """
        job_list = []
        for action in [self.outer_server._serve_forever, self._fetch_results, self._send_task_to_worker]:
            job = gevent.spawn(action)
            job_list.append(job)

        for job in job_list:
            job.join()

    def _fetch_results(self):
        """
        从result server那拿数据
        :return:
        """

        ctx = zmq.Context()
        self.zmq_pub_client = ctx.socket(zmq.SUB)
        self.zmq_pub_client.connect(self.result_address)
        self.zmq_pub_client.setsockopt(zmq.SUBSCRIBE, self.worker_uuid)

        while True:
            msg_part_list = self.zmq_pub_client.recv_multipart()

            for msg_part in msg_part_list:
                task = gw_pb2.Task()
                task = task.ParseFromString(msg_part[1])

                conn = self.conn_dict.get(task.client_id)
                if conn:
                    conn.write(task.data)

    def _send_task_to_worker(self):
        """
        将任务发送到worker
        :return:
        """

        while True:
            task = self.task_queue.get()
            self.zmq_pull_server.send_string(task.SerializeToString())

    def _register_server_handlers(self):
        """
        注册server的一些回调
        :return:
        """

        @self.outer_server.create_conn
        def create_conn(conn):
            logger.debug('conn.id: %r', conn.id)
            self.conn_dict[conn.id] = conn

            task = gw_pb2.Task()
            task.client_id = conn.id
            task.proc_id = self.worker_uuid
            task.cmd = constants.CMD_CLIENT_CREATED

            self.task_queue.put(task)

        @self.outer_server.close_conn
        def close_conn(conn):
            # 删除
            logger.debug('conn.id: %r', conn.id)
            self.conn_dict.pop(conn.id, None)

            task = gw_pb2.Task()
            task.client_id = conn.id
            task.proc_id = self.worker_uuid
            task.cmd = constants.CMD_CLIENT_CLOSED

            self.task_queue.put(task)

        @self.outer_server.handle_request
        def handle_request(conn, data):
            # 转发到worker
            logger.debug('conn.id: %r, data: %r', conn.id, data)
            task = gw_pb2.Task()
            task.client_id = conn.id
            task.proc_id = self.worker_uuid
            task.cmd = constants.CMD_CLIENT_REQ
            task.data = data
            self.task_queue.put(task)

    def _worker_run(self):
        """
        在worker里面执行的
        :return:
        """
        setproctitle.setproctitle(self._make_proc_name('gateway:worker'))
        self.worker_uuid = uuid.uuid4().bytes
        self._handle_child_proc_signals()

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