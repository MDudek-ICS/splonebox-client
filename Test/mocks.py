import socket
from queue import Queue
from unittest.mock import Mock

from Splonecli.Api.plugin import Plugin
from Splonecli.Rpc import connection
from Splonecli.Rpc.connection import Connection
from Splonecli.Rpc.msgpackrpc import MsgpackRpc


# noinspection PyProtectedMember
def plug_rpc_connect(plug: Plugin) -> Mock:
    # Check for reference: https://docs.python.org/3/library/unittest.mock.html
    plug._rpc.connect = Mock()
    return plug._rpc.connect


# noinspection PyProtectedMember
def plug_rpc_send(plug: Plugin) -> Mock:
    plug._rpc.send = Mock()
    return plug._rpc.send

# noinspection PyProtectedMember
def connection_socket(con: Connection) -> Mock:
    con._socket = Mock(spec=socket.socket)
    return con._socket


# noinspection PyProtectedMember
def connection_socket_fake_recv(con: Connection) -> Queue:
    con._socket = Mock(spec=socket.socket)
    q = Queue(maxsize=1)
    con._socket.recv = q.get
    return q


# noinspection PyProtectedMember
def connection_listen_thread(con: Connection) -> Mock:
    con.start_new_thread = Mock()
    return con.start_new_thread


# noinspection PyProtectedMember
def rpc_connection_send(mprpc: MsgpackRpc) -> Mock:
    mprpc._connection.send_message = Mock()
    return mprpc._connection.send_message


# noinspection PyProtectedMember
def rpc_dispatch(mprpc: MsgpackRpc) -> Mock:
    mprpc._dispatcher.dispatch = Mock()
    return mprpc._dispatcher.dispatch


# noinspection PyProtectedMember
def rpc_handle_response(mprpc: MsgpackRpc) -> Mock:
    mprpc._handle_response = Mock()
    return mprpc._handle_response


# noinspection PyProtectedMember
def rpc_handle_notify(mprpc: MsgpackRpc) -> Mock:
    mprpc._handle_notify = Mock()
    return mprpc._handle_notify


def rpc_send(mprpc: MsgpackRpc) -> Mock:
    mprpc.send = Mock()
    return mprpc.send


def receive(plug: Plugin):
    pass
