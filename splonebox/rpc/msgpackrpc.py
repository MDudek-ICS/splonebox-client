"""
This file is part of the splonebox python client library.

The splonebox python client library is free software: you can
redistribute it and/or modify it under the terms of the GNU Lesser
General Public License as published by the Free Software Foundation,
either version 3 of the License or any later version.

It is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this splonebox python client library.  If not,
see <http://www.gnu.org/licenses/>.

"""

import logging

import msgpack

from splonebox.rpc.connection import Connection
from splonebox.rpc.message import Message, InvalidMessageError, MResponse, MNotify


class MsgpackRpc:
    def __init__(self):
        self._connection = Connection()

        self._dispatcher = {}
        self._response_callbacks = {}
        self._unpacker = msgpack.Unpacker()

    def connect(self, host: str, port: int):
        """Connect to given host

        :param host: Hostname to connect to
        :param port: Port to connect to
        :raises: :ConnectionRefusedError if socket is unable to connect
        :raises: :socket.gaierror if Host unknown
        :raises: :ConnectionError if hostname or port are invalid types
        """
        self._connection.connect(host, port, self._message_callback)

    def send(self, msg: Message, response_callback=None):
        """Sends the given message to the server

        :param msg: message to send
        :param response_callback: a function that will be called on response
        :raises :InvalidMessageError if msg.pack() is not possible
        :raises :BrokenPipeError if connection is not established
        :return: None
        """

        if not isinstance(msg, Message):
            raise InvalidMessageError("Unable to send None!")

        if response_callback is not None:
            if msg.get_msgid() is None:
                raise InvalidMessageError(
                    "Notify message does not support responses")

            self._response_callbacks[msg.get_msgid()] = response_callback

        logging.info("sending: \n" + msg.__str__())
        self._connection.send_message(msg.pack())

        # if response callback is None we don't expect a response

    def _message_callback(self, data: bytes):
        """Handles incoming Messages, is called by :Connection

        :param data: Msgpack serialized message
        """
        self._unpacker.feed(data)

        messages = []
        for unpacked in self._unpacker:
            try:
                messages.append(Message.from_unpacked(unpacked))
            except InvalidMessageError as e:
                m = MResponse(0)
                m.error = [400, "Invalid Message Format" + e.__str__()]
                self.send(m)

        if len(messages) == 0:
            logging.info("Received incomplete message from Server: \n" +
                         str(data))
            return

        for msg in messages:
            try:
                logging.info('Received this message: \n' + msg.__str__())
                if msg.get_type() == 0:
                    # type == 0  => Message is request
                    error, response = self._dispatcher[msg.function](msg)
                    rsp = MResponse(msg.get_msgid())
                    rsp.error = error
                    rsp.response = response
                    self.send(rsp)
                elif msg.get_type() == 1:
                    self._handle_response(msg)
                elif msg.get_type() == 2:
                    self._handle_notify(msg)

            except InvalidMessageError as e:
                logging.info(e.name)
                logging.info("\n Unable to handle Message\n")
                if msg.get_type() != 0:
                    return

                m = MResponse(msg.get_msgid())
                m.error = [400, "Could not handle request! " + e.name]
                self.send(m)

            except Exception as e:
                logging.warning("Unexpected exception occurred!")
                logging.warning(e.__str__())
                if msg.get_type() != 0:
                    return
                m = MResponse(msg.get_msgid())
                m.error = [418, "Unexpected exception occurred!"]
                self.send(m)

    def register_function(self, foo, name: str):
        """Register a function at msgpack rpc dispatcher

        :param name: Name of the function
        :param foo: A function reference
        :raises DispatcherError
        """
        self._dispatcher[name] = foo

    def disconnect(self):
        """Disconnect from server"""
        self._connection.disconnect()

    def listen(self):
        """Blocks until connection is closed"""
        self._connection._disconnected.wait()

    def _handle_response(self, msg: MResponse):
        """Handler for response messages (called by _message_callback)

        :param msg: MResponse
        :return:
        """
        try:
            self._response_callbacks.pop(msg.get_msgid())(msg)
        except Exception:
            if msg.error is not None:
                logging.warning("Received error unrelated to any message!\n" +
                                msg.error.__str__())
            else:
                logging.warning(
                    "The msgid in given response does not match any request!\n")
            raise

    def _handle_notify(self, msg: MNotify):
        self._dispatcher["broadcast"](msg)
