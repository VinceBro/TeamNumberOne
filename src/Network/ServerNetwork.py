import json
import socket
import socketserver
import threading
import time

from Network.NetworkState import CommandNetwork
from Utils.Logger import LogError


NETWORK_UPDATE_PERIOD_S = .02


class ServerTCPHandler(socketserver.BaseRequestHandler):
    controller = None

    @LogError
    def handle(self):
        _player_name = 'Unknown'
        _is_spectator = False
        try:
            b_msg = self.request.recv(65535)
            _msg_recv = json.loads(b_msg.decode('utf-8'))
            _player_name = _msg_recv[CommandNetwork.CMD_TRY_CONNEXION]
            if ServerTCPHandler.controller.is_player_already_connected(_player_name):
                print('> [ERROR][{}] Player is already connected ({})'.format('{}:{}'.format(self.client_address[0],
                                                                                             self.client_address[1]),
                                                                              _player_name))
                _player_name = 'Unknown'
                self.request.sendall(json.dumps({CommandNetwork.CMD_CONNEXION_REFUSED: 'Player is already connected'}).encode('utf-8'))
                self.request.shutdown(socket.SHUT_RD)
                self.request.close()
            else:
                self.request.sendall(json.dumps({CommandNetwork.CMD_CONNEXION_OK: 'Player is created'}).encode('utf-8'))
                self.controller.create_player(_player_name)
                print('> Player connected: [{1}] {0} '.format(_player_name, '{}:{}'.format(self.client_address[0],
                                                                                           self.client_address[1])))
                try:
                    while True:
                        b_msg = self.request.recv(65535)
                        if b_msg == b'':
                            break
                        _msg_recv = json.loads(b_msg.decode('utf-8'))
                        # ***** HANDLE UPDATE PLAYER MODEL *****
                        if CommandNetwork.CMD_UPDATE_STATUS in _msg_recv:
                            if not _is_spectator:
                                ServerTCPHandler.controller.update_player_model(_player_name,
                                                                                _msg_recv[CommandNetwork.GAME_INFO],
                                                                                _msg_recv[CommandNetwork.PLAYER_INFO],
                                                                                )
                            time.sleep(NETWORK_UPDATE_PERIOD_S)
                            _msg_send = ServerTCPHandler.controller.get_model_party(_msg_recv[CommandNetwork.GAME_INFO],
                                                                                    _player_name)
                            self.request.sendall(json.dumps(_msg_send).encode('utf-8'))

                        # ***** HANDLE CREATE PARTY *****
                        elif CommandNetwork.CMD_CREATE_PARTY in _msg_recv:
                            try:
                                _party_name, _party_limit, *_ = _msg_recv[CommandNetwork.CMD_CREATE_PARTY]
                                pkg = dict()
                                if ServerTCPHandler.controller.is_party_exist(_party_name, _party_limit, _player_name):
                                    pkg[CommandNetwork.CMD_CREATE_PARTY_OK] = 'No prob bro !'
                                else:
                                    pkg[CommandNetwork.CMD_CREATE_PARTY_REFUSED] = 'Party already exists'
                                self.request.sendall(json.dumps(pkg).encode('utf-8'))
                            except Exception as e:
                                print('> [ERR][{}:{}] {} | {}:{} | pkg: {}'.format(self.client_address[0],
                                                                                   self.client_address[1],
                                                                                   _player_name,
                                                                                   type(e).__name__,
                                                                                   str(e),
                                                                                   _msg_recv))

                        # ***** HANDLE GET PARTY LIST *****
                        elif CommandNetwork.CMD_GET_PARTIES in _msg_recv:
                            pkg = dict()
                            pkg[CommandNetwork.CMD_GET_PARTIES] = ServerTCPHandler.controller.get_party_list()
                            self.request.sendall(json.dumps(pkg).encode('utf-8'))

                        # ***** HANDLE JOIN PARTY *****
                        elif CommandNetwork.CMD_JOIN_PARTY in _msg_recv:
                            pkg = dict()
                            ret, msg = ServerTCPHandler.controller.join_party(_msg_recv[CommandNetwork.CMD_JOIN_PARTY],
                                                                              _player_name)
                            if ret:
                                pkg[CommandNetwork.CMD_JOIN_PARTY_OK] = msg
                                _is_spectator = False
                            else:
                                pkg[CommandNetwork.CMD_JOIN_PARTY_REFUSED] = msg
                            self.request.sendall(json.dumps(pkg).encode('utf-8'))
                        elif CommandNetwork.CMD_WATCH_PARTY in _msg_recv:
                            pkg = dict()
                            ret, msg = ServerTCPHandler.controller.watch_party(_msg_recv[CommandNetwork.CMD_WATCH_PARTY],
                                                                               _player_name)
                            if ret:
                                pkg[CommandNetwork.CMD_JOIN_PARTY_OK] = msg
                                _is_spectator = True
                            else:
                                pkg[CommandNetwork.CMD_JOIN_PARTY_REFUSED] = msg
                            self.request.sendall(json.dumps(pkg).encode('utf-8'))
                finally:
                    self.controller.delete_player(_player_name)
        finally:
            print('> Player disconnect: [{1}] {0} '.format(_player_name, '{}:{}'.format(self.client_address[0],
                                                                                        self.client_address[1])))


class ServerNetwork(threading.Thread):
    def __init__(self, controller):
        threading.Thread.__init__(self)
        self.controller = controller
        ServerTCPHandler.controller = controller
        self._host = None
        self._port = None

    def set_connexion(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    @LogError
    def run(self) -> None:
        with socketserver.ThreadingTCPServer((self._host, self._port), ServerTCPHandler) as server:
            server.serve_forever()
