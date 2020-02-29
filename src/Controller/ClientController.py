import numpy as np

from multiprocessing import Event

from Workspace.Interface.ClientInterface import ClientInterface
from Model.MotionModel import MotionModel
from Model.PartyModel import PartyKey, PartyModel, PartyState
from Network.NetworkState import CommandNetwork as Cmd
from Controller.BaseController import BaseController
from Network.ClientNetwork import ClientNetwork
from View.MainView import MainView


class ClientController(BaseController, ClientInterface):
    def __init__(self, workspace):
        self._player_name = 'unknown'

        self.motion_command = MotionModel()
        self.party = PartyModel('', 0)
        self.network = ClientNetwork(self)
        self.view = MainView(self)
        self.workspace = workspace(self)

        self._flag_network_event = Event()
        self._flag_network_event.clear()

    # -------------------- CONTROLLER CORE --------------------
    def get_name(self):
        return self._player_name

    def set_player_name(self, name: str) -> None:
        self._player_name = name

    def set_connexion_info(self, host: str, port: int) -> None:
        self.network.set_connexion(host, port)

    def start(self) -> None:
        self.network.start()
        self.view.start()
        self.workspace.start()

    def join(self) -> None:
        self.network.stop()

    def stop(self):
        self.join()
        self.view.close()

    def set_network_event(self):
        self._flag_network_event.set()

    def clear_network_event(self):
        self._flag_network_event.clear()

    # -------------------- BUTTON CALL BACK --------------------
    def callback_join_party(self):
        _party_name = self.view.get_party_selected()
        if _party_name is not None:
            self.watch_party(_party_name)

    def callback_watch_party(self):
        _party_name = self.view.get_party_selected()
        if _party_name is not None:
            self.join_party(_party_name)

    def callback_show_party_list(self):
        self.view.show_parties_list()

    def callback_show_party_form(self):
        self.view.show_party_form()

    # -------------------- NETWORK FUNC --------------------
    def get_parties_from_server(self) -> list:
        return self.network.get_party_list()

    def join_party(self, party_name):
        if self.network.watch_party(party_name):
            self.party = PartyModel(party_name)
            self.change_mode_to_playing()

    def watch_party(self, party_name):
        if self.network.join_party(party_name):
            self.party = PartyModel(party_name)
            self.change_mode_to_playing()

    def create_party(self, party_model):
        if self.network.create_party(party_model):
            _name, _limit, _player = party_model
            self.party = PartyModel(_name, _limit)
            self.callback_show_party_list()

    def wait_until_event(self) -> bool:
        _resp = self._flag_network_event.wait(timeout=1)
        self.clear_network_event()
        return _resp

    # -------------------- CLIENT MODEL --------------------
    def get_update_model(self) -> dict:
        return {Cmd.CMD_UPDATE_STATUS: self._player_name,
                Cmd.PLAYER_INFO: self.motion_command.to_dict(),
                Cmd.GAME_INFO: self.party.name,
                }

    def update_party(self, model: dict) -> None:
        try:
            if not self.party.name == model[PartyKey.KEY_NAME]:
                self.party = PartyModel(model[PartyKey.KEY_NAME], model[PartyKey.KEY_LIMIT])

            self.party.update(model)
        except Exception as e:
            print('> [ERR] update party: {}: {}'.format(type(e).__name__, e))

    # -------------------- VIEW CONTROL --------------------
    def change_mode_to_playing(self):
        self.view.show_playing_mode()
        self.network.set_ping_pong_mode()

    def change_mode_to_menu(self):
        self.view.show_parties_list()
        self.network.set_sender_mode()
        self.callback_show_party_list()

    # -------------------- PARTY FUNC --------------------
    # >> PARTY MOBILE OBJECTS
    def get_mobs_in_radius(self, near_point: np.ndarray, radius: int, enemy_only=True):
        if enemy_only:
            return [_mob for _mob in self.party.get_mobs_iterator() if np.linalg.norm(_mob.xy - near_point) < radius and
                    not _mob.name == self.get_name()]
        else:
            return [_mob for _mob in self.party.get_mobs_iterator() if np.linalg.norm(_mob.xy - near_point) < radius]

    def get_data_from_players(self, enemy_only=False):
        if enemy_only:
            return [_player for _player in self.party.get_players_iterator() if not _player.name == self.get_name()]
        else:
            return self.party.get_players_iterator()

    def get_data_from_asteroids(self):
        return self.party.get_asteroids_iterator()

    def get_data_from_bolts(self):
        return self.party.get_bolts_iterator()

    def get_player(self, name: str):
        return self.party.get_player(name)

    def get_players_name(self):
        return self.party.get_players_name()

    def get_asteroid(self, name: str):
        return self.party.get_asteroid(name)

    def get_data_from_mobs(self, enemy_only=False):
        if enemy_only:
            return [_mob for _mob in self.party.get_mobs_iterator() if not _mob.name == self.get_name()]
        return self.party.get_mobs_iterator()

    def is_spectator(self):
        return not self.get_name() in self.party.get_players_name()

    # >> PLAYER MOTION
    def set_motion_command(self, motion: MotionModel):
        self.motion_command = motion

    def get_motion_from_party(self):
        try:
            return self.party.motions[-1]
        except:
            return dict()

    # >> PARTY MODEL
    def get_time_left(self):
        return self.party.get_time_left()

    def get_dead_zone_radius(self):
        return self.party.get_dead_zone_radius()

    def get_dead_zone_center(self):
        return self.party.get_dead_zone_center()

    def get_winner(self):
        return self.party.dead_pool[-1]

    def get_rank_board(self):
        return self.party.dead_pool

    # >> PARTY STATES
    def is_party_done(self):
        try:
            return self.party.is_done()
        except Exception as e:
            return False

    def is_party_waiting(self):
        return self.party.state == PartyState.STATE_WAITING_FOR_PLAYERS

    def is_party_ready_to_fight(self):
        return self.party.state == PartyState.STATE_READY_TO_FIGHT

    def is_party_in_progress(self):
        return self.party.state == PartyState.STATE_IN_PROGRESS

    def has_party_winner(self):
        return self.party.state == PartyState.STATE_WINNER

    def get_party_name(self):
        return self.party.name
