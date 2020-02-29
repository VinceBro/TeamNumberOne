import argparse
import sys

from PySide2.QtWidgets import QApplication

from Workspace.myWorkspace import myWorkspace
from Workspace.myWorkspace import myWorkspace

__author__ = "Julien Becirovski <j.becirovski@protolabquebec.ca>"

from Controller.ClientController import ClientController
from Controller.ServerController import ServerController


class ArgType:
    T_CLIENT = 'client'
    T_SERVER = 'server'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='IEEE Student competition')
    parser.add_argument('pseudo', type=str, help='Your player name.')
    parser.add_argument('type', type=str, choices=[ArgType.T_CLIENT, ArgType.T_SERVER],
                        help='Your session type (client or server).')
    parser.add_argument('--port', type=int, default=8000, help='Server port (Ex: 80).')
    parser.add_argument('--ip', type=str, default='localhost', help='Server ip (Ex: 127.0.0.1).')

    args = parser.parse_args()
    if args.type == ArgType.T_CLIENT:
        print('***** GAME CLIENT START *****')
        app = QApplication(sys.argv)
        client = ClientController(myWorkspace)
        # client = ClientController(myWorkspace)
        client.set_player_name(args.pseudo)
        print('> player created: {}'.format(args.pseudo))
        client.set_connexion_info(args.ip, args.port)
        print('> player listen: [{}:{}]'.format(args.ip, args.port))
        client.start()
        result = app.exec_()
        client.network.stop()
        print('***** GAME CLIENT ENDED *****')
        exit(result)

    elif args.type == ArgType.T_SERVER:
        print('***** GAME SERVER START *****')
        server = ServerController()
        server.set_connexion_info(args.ip, args.port)
        print('> server created: [{}:{}]'.format(args.ip, args.port))
        server.start()
        print('> server start...')
        server.join()
        print('***** GAME SERVER ENDED *****')
