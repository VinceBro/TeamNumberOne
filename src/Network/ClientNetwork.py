import json
import sys
import threading, socket
import time
from json import JSONDecodeError

from Network.NetworkState import PlayerMode, CommandNetwork


class ClientNetwork(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller
        self._host = None
        self._port = None
        self._is_running = False
        self._mode = PlayerMode.MODE_SENDER
        self.client = None

    def get_pkg_try_connexion(self):
        return {CommandNetwork.CMD_TRY_CONNEXION: self.controller.get_name()}

    def run(self) -> None:
        try:
            assert None not in [self._host, self._port], 'You must set connexion parameters ({}:{})'.format(self._host,
                                                                                                            self._port)

            self._is_running = True
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                self.client = client
                client.connect((self._host, self._port))
                client.sendall(self.encode(self.get_pkg_try_connexion()))
                _resp = b''
                _is_running = True
                while _is_running:
                    try:
                        _resp = self.listen(append=_resp)
                        server_response = self.decode(_resp)
                        # print(len(_resp), _resp, file=sys.stderr)
                        _is_running = False
                    except Exception as e:
                        # print('too short {}'.format(type(e).__name__), file=sys.stderr)
                        continue
                self.controller.set_network_event()
                if CommandNetwork.CMD_CONNEXION_REFUSED in server_response:
                    print('[ERROR] Server: {}'.format(server_response[CommandNetwork.CMD_CONNEXION_REFUSED]))
                    self._is_running = False
                    time.sleep(1)
                    self.controller.stop()
                else:
                    print('> player is connected')
                    i = 0
                    while self._is_running:
                        i += 1
                        if self._mode == PlayerMode.MODE_PING_PONG:
                            client_model = self.controller.get_update_model()
                            client.sendall(self.encode(client_model))
                            server_pkg = ''
                            _is_running = True
                            _msg = b''
                            while _is_running:
                                try:
                                    _msg = self.listen(append=_msg)
                                    server_pkg = self.decode(_msg)
                                    _is_running = False
                                except JSONDecodeError as e:
                                    # print('too short {}'.format(type(e).__name__), file=sys.stderr)
                                    continue
                            self.controller.set_network_event()
                            self.controller.update_party(server_pkg)
                            if self.controller.is_party_done():
                                self.controller.change_mode_to_menu()
                        elif self._mode == PlayerMode.MODE_SENDER:
                            time.sleep(.25)
                        else:
                            print('> player disconnected')
                            break
        except Exception as e:
            print('> [ERR] Network | [{}]: {}'.format(type(e).__name__, e))
        finally:
            self.client = None
            self._is_running = False
            self.controller.stop()

    def set_connexion(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    def encode(self, message: dict) -> bytes:
        return json.dumps(message).encode('utf-8')

    def decode(self, message: bytes):
        return json.loads(message.decode('utf-8'))

    def listen(self, append=b'') -> bytes:
        _pkg = append + self.client.recv(65535)
        return _pkg

    def send(self, message: bytes) -> None:
        self.client.sendall(message)

    def call(self, message):
        self.send(self.encode(message))
        _msg = b''
        while True:
            try:
                _msg = self.listen(append=_msg)
                _resp = self.decode(_msg)
                # print(len(_msg), _msg, file=sys.stderr)
                return _resp
            except Exception as e:
                # print('too short {}'.format(type(e).__name__), file=sys.stderr)
                continue

    def create_party(self, party_model) -> bool:
        if self.client is not None:
            _pkg = {CommandNetwork.CMD_CREATE_PARTY: party_model}
            self.send(self.encode(_pkg))
            _msg = b''
            _is_running = True
            resp = []
            while _is_running:
                try:
                    _msg = self.listen(append=_msg)
                    resp = self.decode(_msg)
                    _is_running = False
                except Exception as e:
                    continue

            self.controller.set_network_event()
            if CommandNetwork.CMD_CREATE_PARTY_REFUSED in resp:
                print('> Server refused to create your party : {}'.format(resp[CommandNetwork.CMD_CREATE_PARTY_REFUSED]))
                return False
            elif CommandNetwork.CMD_CREATE_PARTY_OK in resp:
                print('> Server create your party')
                return True
            else:
                print('> Server error: {}'.format(resp))
                return False
        else:
            print('> [ERR] Network | Client is not set.')
            return False

    def set_ping_pong_mode(self):
        self._mode = PlayerMode.MODE_PING_PONG

    def set_sender_mode(self):
        self._mode = PlayerMode.MODE_SENDER

    def get_party_list(self) -> list:
        if self.client is not None:
            _pkg = {CommandNetwork.CMD_GET_PARTIES: ''}
            _parties = []
            try:
                _pkg = self.call(_pkg)
                self.controller.set_network_event()
                assert CommandNetwork.CMD_GET_PARTIES in _pkg
                _parties = _pkg.get(CommandNetwork.CMD_GET_PARTIES)
            finally:
                return _parties
        return list()

    def join_party(self, party_name) -> bool:
        if self.client is not None:
            _pkg = {CommandNetwork.CMD_JOIN_PARTY: party_name}
            _pkg = self.call(_pkg)
            self.controller.set_network_event()
            if CommandNetwork.CMD_JOIN_PARTY_OK in _pkg:
                print('> Player join party')
                return True
            elif CommandNetwork.CMD_JOIN_PARTY_REFUSED in _pkg:
                print('> Server refuse to join party: {}'.format(_pkg[CommandNetwork.CMD_JOIN_PARTY_REFUSED]))
                return False
        return False

    def watch_party(self, party_name) -> bool:
        if self.client is not None:
            _pkg = {CommandNetwork.CMD_WATCH_PARTY: party_name}
            _pkg = self.call(_pkg)
            self.controller.set_network_event()
            if CommandNetwork.CMD_JOIN_PARTY_OK in _pkg:
                print('> Player spec party')
                return True
            elif CommandNetwork.CMD_JOIN_PARTY_REFUSED in _pkg:
                print('> Server refuse to join party: {}'.format(_pkg[CommandNetwork.CMD_JOIN_PARTY_REFUSED]))
                return False
        return False

    def stop(self):
        self._mode = PlayerMode.MODE_QUIT
