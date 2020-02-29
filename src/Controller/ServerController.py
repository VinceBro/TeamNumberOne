import random
import traceback

import numpy as np
import matplotlib.colors as colors
import time

from PySide2.QtCore import QThread

from Model.AsteroidModel import AsteroidModel
from Model.BoltModel import BoltModel
from Model.MotionModel import MotionModel, MotionState
from Network.NetworkState import CommandNetwork as Cmd
from Controller.BaseController import BaseController
from Network.ServerNetwork import ServerNetwork
from Model.ShipModel import ShipModel
from Model.PartyModel import PartyState, PartyKey, PartyConst, PartyModel
from Utils.Logger import LogError
from Model.ModelType import ModelType

DEBUG_MODE = False
DEBUG_DISPLAY_PERIOD_S = .2
SERVICE_REAL_TIME_PERIOD_S = 0.02
SERVICE_STATE_PERIOD_S = 0.5
SERVICE_TIME_LEFT_PERIOD_S = 1


class TimerSettings:
    KEY_SHOOT = 'k_shoot'
    TIMER_SHOOT_PERIOD_S = .25


class ServerController(BaseController):
    def __init__(self):
        self.network = ServerNetwork(self)
        self.hosted_parties = dict()
        self.hosted_players = set()
        self.core_timers = {TimerSettings.KEY_SHOOT: dict()}

        self.players = dict()

        # Async handlers
        self.services_are_running = True
        self.thread_services = list()
        self.init_services()

        # Async variable
        self.create_asteroid = 0

    def init_services(self):
        thread_service_timeleft = QThread()
        thread_service_timeleft.run = self.service_party_time_left

        thread_service_motion = QThread()
        thread_service_motion.run = self.service_party_motion

        thread_service_collision = QThread()
        thread_service_collision.run = self.service_party_collision

        thread_service_states = QThread()
        thread_service_states.run = self.service_party_states

        thread_service_debug = QThread()
        thread_service_debug.run = self.service_debug

        self.thread_services.append(thread_service_motion)
        self.thread_services.append(thread_service_collision)
        self.thread_services.append(thread_service_states)
        self.thread_services.append(thread_service_timeleft)
        self.thread_services.append(thread_service_debug)

    def start(self):
        self.network.start()
        for _service in self.thread_services:
            _service.start()

    def join(self):
        self.network.join()
        self.join_services()

    def join_services(self):
        self.services_are_running = False
        for _service in self.thread_services:
            _service.terminate()
            _service.wait()

    def set_connexion_info(self, host: str, port: int):
        self.network.set_connexion(host, port)

    # -------------------- SERVER MODEL --------------------
    def update_player_model(self, name, party, motion):
        self.hosted_parties[party][PartyKey.KEY_MOTION][name] = MotionModel().from_dict(motion)

    def get_model_player(self, name):
        return self.players[name].to_dict()

    def get_model_party(self, party_name, player):
        _party = self.hosted_parties.get(party_name)
        if _party is None:
            _party = PartyModel.get_ended_pkg(party_name, player)
        _party_cp = _party.copy()
        _party_cp[PartyKey.KEY_MOBS] = {PartyKey.KEY_MOB_PLAYERS: [_mob.to_dict() for _mob in _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS]],
                                        PartyKey.KEY_MOB_ASTEROIDS: [_mob.to_dict() for _mob in _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS]],
                                        PartyKey.KEY_MOB_BOLTS: [_mob.to_dict() for _mob in _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_BOLTS]]}
        _party_cp[PartyKey.KEY_MOTION] = {_player: _motion.to_dict() for _player, _motion in _party[PartyKey.KEY_MOTION].items()}
        _party_cp[PartyKey.KEY_DEAD_ZONE] = _party[PartyKey.KEY_DEAD_ZONE].copy()
        _party_cp[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_CENTER] = _party[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_CENTER].tolist()
        return _party_cp

    def get_players(self):
        return [_model.to_dict() for _model in self.players.values()]

    def get_model(self, player_name: str):
        _model = self.get_players()
        _server_model = dict()
        _server_model[Cmd.MOBILE_OBJECTS_INFO] = _model
        _server_model[Cmd.GAME_INFO] = 'unknown'
        _server_model[Cmd.PLAYER_INFO] = self.get_model_player(player_name)
        return _server_model

    def is_player_already_connected(self, player):
        return player in self.hosted_players

    @LogError
    def create_player(self, player):
        self.hosted_players.add(player)

    @LogError
    def delete_player(self, player):
        self.hosted_players.remove(player)

    def is_party_exist(self, name: str, limit: int, creator: str) -> bool:
        if name in self.hosted_parties:
            return False
        self.hosted_parties[name] = {PartyKey.KEY_LIMIT: limit, PartyKey.KEY_PLAYERS: dict(),
                                     PartyKey.KEY_MOBS: {PartyKey.KEY_MOB_PLAYERS: list(),
                                                         PartyKey.KEY_MOB_BOLTS: list(),
                                                         PartyKey.KEY_MOB_ASTEROIDS: list()},
                                     PartyKey.KEY_CREATED: time.time(),
                                     PartyKey.KEY_CREATOR: creator,
                                     PartyKey.KEY_STATE: PartyState.STATE_WAITING_FOR_PLAYERS,
                                     PartyKey.KEY_PREV_STATE: PartyState.STATE_INIT,
                                     PartyKey.KEY_TIME_LEFT: PartyConst.TIME_MAX_WAITING,
                                     PartyKey.KEY_NAME: name,
                                     PartyKey.KEY_MOTION: dict(),
                                     PartyKey.KEY_DEAD_POOL: list(),
                                     PartyKey.KEY_DEAD_ZONE: {PartyKey.KEY_DEAD_ZONE_RADIUS: PartyConst.DEAD_ZONE_MAX_RADIUS,
                                                              PartyKey.KEY_DEAD_ZONE_CENTER: np.array([0, 0])},
                                     }
        return True

    def get_party_list(self) -> list:
        return [(_name, '{}/{}'.format(len(_model[PartyKey.KEY_PLAYERS]), _model[PartyKey.KEY_LIMIT]), _model[PartyKey.KEY_CREATOR]) for _name, _model in self.hosted_parties.items()]

    def join_party(self, _name, _player) -> tuple:
        if _name not in self.hosted_parties:
            print('> Player {} try to join an unknown party ({})'.format(_player, _name))
            return False, 'Party is unknown'

        if len(self.hosted_parties[_name][PartyKey.KEY_PLAYERS]) >= self.hosted_parties[_name][PartyKey.KEY_LIMIT]:
            print('> Player {} try to join a full party ({})'.format(_player, _name))
            return False, 'Party is full'

        if _player in self.hosted_parties[_name][PartyKey.KEY_PLAYERS]:
            print('> Player {} is already in this party ({})'.format(_player, _name))
            return False, 'Player is already in this party'

        self.hosted_parties[_name][PartyKey.KEY_PLAYERS][_player] = time.time()
        print('> Player {} join party {}'.format(_player, _name))
        return True, 'Have fun !'

    def watch_party(self, _name, _player) -> tuple:
        if _name not in self.hosted_parties:
            print('> Player {} try to observe an unknown party ({})'.format(_player, _name))
            return False, 'Party is unknown'

        print('> Player {} watch party {}'.format(_player, _name))
        return True, 'Have fun watcher !'

    def delete_party(self, name):
        del self.hosted_parties[name]
        print('> Server: Party {} has been deleted'.format(name))

    def startup_party_elements(self, party_name):
        _party = self.hosted_parties[party_name]
        assert _party[PartyKey.KEY_LIMIT] > 0, 'Party is set with player limit at zero (0)'
        _color_part = 1 / _party[PartyKey.KEY_LIMIT]

        # PREDEFINE SPAWN (PLAYER AND ASTEROIDS)
        # > Generate player spawns
        _iterative_angle = 2 * np.pi / _party[PartyKey.KEY_LIMIT]
        _player_spawns = [np.array([np.cos(_i * _iterative_angle), np.sin(_i * _iterative_angle)]) *
                                   (PartyConst.DEAD_ZONE_MAX_RADIUS / 2) for _i in range(_party[PartyKey.KEY_LIMIT])]
        random.shuffle(_player_spawns)

        # > Generate asteroid spawns to hide sight
        _asteroid_spawns = []
        for _i, _p_spawn in enumerate(_player_spawns):
            for _p_spawn_2 in _player_spawns[_i+1:]:
                _dist = np.linalg.norm(_p_spawn - _p_spawn_2)
                if _dist == 0:  # When is the same spawn point
                    continue
                _dir = (_p_spawn_2 - _p_spawn) / _dist
                _asteroid_pst = _p_spawn + _dir * _dist // 2
                _asteroid_spawns.append(_asteroid_pst)

        # > Create Ship for players
        for _i, (_spawn, _player) in enumerate(zip(_player_spawns, _party[PartyKey.KEY_PLAYERS])):
            try:
                np.random.seed(int(time.time())+_i)
                _ship = ShipModel()
                _ship.name = _player
                _ship.color = (colors.hsv_to_rgb([_i * _color_part, 1, 1]) * 255).tolist()
                _ship.set_angle(np.random.randint(0, 359))
                _ship.set_position(_spawn)
                _ship.set_speed(np.array([0, 0]))
                _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS].append(_ship)
            except Exception as e:
                print("> [ERR] startup party players > {}: {}".format(type(e).__name__, e))

        # > Create asteroid
        for _asteroid_spawn in _asteroid_spawns:
            try:
                _asteroid = AsteroidModel(radius=np.random.randint(50, 150))
                _asteroid.set_angle(np.random.randint(0, 359))
                _asteroid.set_speed(np.array([np.random.randint(2, 10), 0]))
                _asteroid.set_position(_asteroid_spawn)
                _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS].append(_asteroid)
            except Exception as e:
                print("> [ERR] startup party asteroid > {}: {}".format(type(e).__name__, e))

    # -------------------- SERVICES --------------------
    def service_party_motion(self):
        """ Update motion """
        _service_name = 'Service::Motion'
        print('> {} is running...'.format(_service_name))
        while self.services_are_running:
            _begin = time.time()
            try:
                for _name, _party in self.hosted_parties.items():
                    if not _party[PartyKey.KEY_STATE] == PartyState.STATE_IN_PROGRESS:
                        continue

                    # DEAD ZONE CIRCLE
                    _dt_radius = PartyConst.DEAD_ZONE_MAX_RADIUS / PartyConst.TIME_MAX_DEAD_ZONE * SERVICE_REAL_TIME_PERIOD_S
                    _party[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_RADIUS] -= _dt_radius
                    if _party[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_RADIUS] < 0:
                        _party[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_RADIUS] = 0

                    _all_mobs = _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS] + _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_BOLTS] + _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS]
                    for _mob in _all_mobs:
                        if _mob.is_alive and _mob.type == ModelType.SHIP_MODEL:
                            _command = _party[PartyKey.KEY_MOTION].get(_mob.name)
                            _prop_ppm = 0
                            _rot_ppm = 0
                            if _command is not None:
                                if _command.state == MotionState.STATE_MOVE:
                                    _prop_ppm = _mob.get_propulsion_speed() + _command.acceleration * PartyConst.MOTION_MAX_PROPULSION_ACCEL
                                    _rot_ppm = _command.rotation * PartyConst.MOTION_MAX_ROTATION_ACCEL
                                elif _command.state == MotionState.STATE_STOP:
                                    _prop_ppm = _mob.get_propulsion_speed() - 1. * PartyConst.MOTION_MAX_PROPULSION_ACCEL
                                    _rot_ppm = 0
                                elif _command.state == MotionState.STATE_SHOOT:
                                    _shoot_dir = _command.shoot_xy
                                    _bolt = self.start_shoot(_mob, _shoot_dir)
                                    _prop_ppm = _mob.get_propulsion_speed()
                                    _rot_ppm = 0
                                    if _bolt is not None:
                                        _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_BOLTS].append(_bolt)
                                        _prop_ppm = _mob.get_propulsion_speed()
                                        _rot_ppm = _mob.get_rotation_speed()

                            # CROP SPEED LIMIT
                            if PartyConst.MOTION_MAX_PROPULSION_SPEED < _prop_ppm:
                                _prop_ppm = PartyConst.MOTION_MAX_PROPULSION_SPEED

                            if _prop_ppm < PartyConst.MOTION_MIN_PROPULSION_SPEED:
                                _prop_ppm = PartyConst.MOTION_MIN_PROPULSION_SPEED

                            if PartyConst.MOTION_MAX_ROTATION_SPEED < _rot_ppm:
                                _rot_ppm = PartyConst.MOTION_MAX_ROTATION_SPEED

                            if _rot_ppm < PartyConst.MOTION_MIN_ROTATION_SPEED:
                                _rot_ppm = PartyConst.MOTION_MIN_ROTATION_SPEED

                            # SET POSITION INCREMENT
                            _dt_prop = _prop_ppm * SERVICE_REAL_TIME_PERIOD_S
                            _dt_rot = _rot_ppm * SERVICE_REAL_TIME_PERIOD_S
                            _mob.set_dir(np.dot(np.array([[np.cos(_dt_rot), -np.sin(_dt_rot)],
                                                          [np.sin(_dt_rot), np.cos(_dt_rot)]]),
                                                _mob.dir))
                            _mob.set_position(_mob.xy + _mob.dir * _dt_prop)
                            _mob.set_speed(np.array([_prop_ppm, _rot_ppm]))
                        else:
                            _mob.set_position(_mob.xy + _mob.dir * _mob.get_propulsion_speed() * SERVICE_REAL_TIME_PERIOD_S)

                    if _party[PartyKey.KEY_STATE] not in [PartyState.STATE_IN_PROGRESS,
                                                          PartyState.STATE_WINNER]:
                        continue

                    #  > Asteroid condition
                    _asteroid_to_create = PartyConst.ASTEROID_COUNT - len(_party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS])
                    for _ in range(_asteroid_to_create):
                        _too_close = True
                        while _too_close:
                            _dir = np.random.uniform(-1, 1, 2)
                            _dir = _dir / np.linalg.norm(_dir)
                            _pst_xy = _dir * PartyConst.ASTEROID_RADIUS_SPAWN

                            _size = np.random.randint(*PartyConst.ASTEROID_SIZE_LIMIT)
                            _speed = np.array([np.random.randint(*PartyConst.ASTEROID_SPEED_LIMIT), 0])

                            _dt_rot = np.random.uniform(-5/180*np.pi, 5/180*np.pi)
                            _dir_xy = _dir * -1
                            _dir_xy = np.array([[np.cos(_dt_rot), -np.sin(_dt_rot)],
                                                [np.sin(_dt_rot), np.cos(_dt_rot)]]).dot(_dir_xy)
                            m_asteroid = AsteroidModel(pst_xy=_pst_xy, dir_xy=_dir_xy, v_xy=_speed,
                                                       radius=_size)
                            _test_proximity = False
                            for _mob in _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS] + _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS]:
                                if np.linalg.norm(_mob.xy - m_asteroid.xy) < (_mob.radius + m_asteroid.radius) // 2:
                                    _test_proximity = True
                                    break

                            if not _test_proximity:
                                _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS].append(m_asteroid)
                                _too_close = False

                _end = time.time()
                _run_time = SERVICE_REAL_TIME_PERIOD_S - (_end - _begin)
                if _run_time > 0:
                    QThread.currentThread().msleep(int(_run_time * 1000))
                else:
                    print('> [WARNING]{}: Runtime {} ms.'.format(_service_name, _run_time * 1000))
            except Exception as e:
                print('ERR: {} > {}:{}'.format(_service_name, type(e).__name__, e))
                traceback.print_exc()

        print('> {} ended'.format(_service_name))

    def service_party_time_left(self):
        """ Update time left """
        _service_name = 'Service::Timeleft'
        print('> {} is running...'.format(_service_name))
        while self.services_are_running:
            try:
                for _name, _party in self.hosted_parties.items():
                    _state = _party[PartyKey.KEY_STATE]
                    if _state == PartyState.STATE_WAITING_FOR_PLAYERS:
                        if _party[PartyKey.KEY_TIME_LEFT] > 0:
                            _party[PartyKey.KEY_TIME_LEFT] -= 1
                        else:
                            print('> Party [{}] change state to [{}]'.format(_name, PartyState.STATE_PARTY_ENDED))
                            _party[PartyKey.KEY_STATE] = PartyState.STATE_PARTY_ENDED
                            _party[PartyKey.KEY_TIME_LEFT] = 10
                    elif _state == PartyState.STATE_READY_TO_FIGHT:
                        if _party[PartyKey.KEY_TIME_LEFT] > 0:
                            _party[PartyKey.KEY_TIME_LEFT] -= 1
                        else:
                            print('> Party [{}] change state to [{}]'.format(_name, PartyState.STATE_IN_PROGRESS))
                            _party[PartyKey.KEY_STATE] = PartyState.STATE_IN_PROGRESS
                            _party[PartyKey.KEY_TIME_LEFT] = 0

                    elif _state == PartyState.STATE_IN_PROGRESS:
                        if _party[PartyKey.KEY_TIME_LEFT] > 0:
                            _party[PartyKey.KEY_TIME_LEFT] -= 1
                        else:
                            print('> Party [{}] change state to [{}]'.format(_name, PartyState.STATE_PARTY_ENDED))
                            _party[PartyKey.KEY_STATE] = PartyState.STATE_PARTY_ENDED
                            _party[PartyKey.KEY_TIME_LEFT] = 0

                    elif _state == PartyState.STATE_WINNER:
                        if _party[PartyKey.KEY_TIME_LEFT] > 0:
                            _party[PartyKey.KEY_TIME_LEFT] -= 1
                        else:
                            print('> Party [{}] change state to [{}]'.format(_name, PartyState.STATE_PARTY_ENDED))
                            _party[PartyKey.KEY_STATE] = PartyState.STATE_PARTY_ENDED
                            _party[PartyKey.KEY_TIME_LEFT] = 10

                QThread.currentThread().msleep(SERVICE_TIME_LEFT_PERIOD_S * 1000)
            except Exception as e:
                pass
        print('> {} ended'.format(_service_name))

    def service_party_collision(self):
        """ Solve collisions """
        _service_name = 'Service::Collision'
        print('> {} is running... '.format(_service_name))
        while self.services_are_running:
            _begin = time.time()
            try:
                for _name, _party in self.hosted_parties.items():

                    if _party[PartyKey.KEY_STATE] in [PartyState.STATE_IN_PROGRESS,
                                                      PartyState.STATE_WINNER]:
                        _all_mobs = _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS] + _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS] + _party[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_BOLTS]
                        for _i, _mob in enumerate(_all_mobs):

                            # Dead zone damage
                            _dt_mob_from_dz_center = np.linalg.norm(_mob.xy - _party[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_CENTER])
                            if _dt_mob_from_dz_center > _party[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_RADIUS]:
                                if _party[PartyKey.KEY_STATE] == PartyState.STATE_IN_PROGRESS:
                                    if _mob.is_alive:
                                        _mob.set_damage(PartyConst.DEAD_ZONE_DAMAGE_PER_S * SERVICE_REAL_TIME_PERIOD_S)
                                        if _mob.type == ModelType.SHIP_MODEL and not _mob.is_alive:
                                            _party[PartyKey.KEY_DEAD_POOL].append(_mob.name)

                            # Detect collision
                            for _collider in _all_mobs[_i:]:
                                if not _collider.name == _mob.name:
                                    _dist = np.linalg.norm(_collider.xy - _mob.xy)
                                    if _dist == 0:
                                        continue
                                    if _dist < (_collider.radius + _mob.radius)/2:
                                        if ModelType.BOLT_MODEL not in [_mob.type, _collider.type]:
                                            # print('COLLISION:', _mob.name, 'with', _collider.name)
                                            # Set position offset after collision
                                            _diff = (_collider.radius + _mob.radius)/2 - _dist
                                            # _diff += 5
                                            _diff_ratio1 = _mob.weight / (_mob.weight + _collider.weight) * _diff
                                            _diff_ratio2 = _collider.weight / (_mob.weight + _collider.weight) * _diff

                                            _mob.set_position(_mob.xy + _diff_ratio2 * (_mob.xy - _collider.xy) / _dist)
                                            _collider.set_position(_collider.xy + _diff_ratio1 * (_collider.xy - _mob.xy) / _dist)

                                            # Set orientation offset after collision
                                            # -- Normal
                                            _normal = (_collider.xy - _mob.xy) / _dist

                                            # -- Tangente
                                            _tx = -_normal[1]
                                            _ty = _normal[0]

                                            # -- dot product tangent
                                            _dp_tan_1 = _mob.dir_x * _mob.get_propulsion_speed() * _tx + _mob.dir_y * _mob.get_propulsion_speed() * _ty
                                            _dp_tan_2 = _collider.dir_x * _collider.get_propulsion_speed() * _tx + _collider.dir_y * _collider.get_propulsion_speed() * _ty

                                            # -- dot product normal
                                            _dp_normal_mob = _mob.dir_x * _mob.get_propulsion_speed() * _normal[0] + _mob.dir_y * _mob.get_propulsion_speed() * _normal[1]
                                            _dp_normal_collider = _collider.dir_x * _collider.get_propulsion_speed() * _normal[0] + _collider.dir_y * _collider.get_propulsion_speed() * _normal[1]

                                            # -- conservation of momentum
                                            _m1 = (_dp_normal_mob * (_mob.weight - _collider.weight) + 2 * _collider.weight * _dp_normal_collider) / (_mob.weight + _collider.weight)
                                            _m2 = (_dp_normal_collider * (_collider.weight - _mob.weight) + 2 * _mob.weight * _dp_normal_mob) / (_mob.weight + _collider.weight)

                                            _speed1 = np.array([_tx*_dp_tan_1+_normal[0]*_m1,
                                                                _ty*_dp_tan_1+_normal[1]*_m1])
                                            _speed2 = np.array([_tx*_dp_tan_2+_normal[0]*_m2,
                                                                _ty*_dp_tan_2+_normal[1]*_m2])

                                            _prop1 = np.linalg.norm(_speed1)
                                            _prop2 = np.linalg.norm(_speed2)

                                            _dir1 = _speed1 / _prop1
                                            _mob.set_dir(_dir1)
                                            _mob.set_speed(np.array([_prop1, _mob.speed[1]]))

                                            _dir2 = _speed2 / _prop2
                                            _collider.set_dir(_dir2)
                                            _collider.set_speed(np.array([_prop2, _collider.speed[1]]))

                                        # SET DAMAGE
                                        if _mob.is_alive:
                                            _mob.set_damage(_collider.damage)
                                            if _mob.type == ModelType.SHIP_MODEL and not _mob.is_alive:
                                                _party[PartyKey.KEY_DEAD_POOL].append(_mob.name)
                                        if _collider.is_alive:
                                            _collider.set_damage(_mob.damage)
                                            if _collider.type == ModelType.SHIP_MODEL and not _collider.is_alive:
                                                _party[PartyKey.KEY_DEAD_POOL].append(_collider.name)

            except Exception as e:
                print('> [ERR] {} | {}:{}'.format(_service_name, type(e).__name__, e))
                traceback.print_exc()

            _end = time.time()
            _run_time = SERVICE_REAL_TIME_PERIOD_S - (_end - _begin)
            if _run_time > 0:
                QThread.currentThread().msleep(int(_run_time * 1000))
        print('> {} ended'.format(_service_name))

    def service_party_states(self):
        """ Solve party states """
        _service_name = 'Service::States'
        print('> {} is running...'.format(_service_name))
        while self.services_are_running:
            try:
                for _name, _model in self.hosted_parties.items():
                    _state = _model[PartyKey.KEY_STATE]
                    if _state == PartyState.STATE_WAITING_FOR_PLAYERS:
                        if len(_model[PartyKey.KEY_PLAYERS]) >= _model[PartyKey.KEY_LIMIT]:
                            print('> Party [{}] change state to [{}]'.format(_name, PartyState.STATE_READY_TO_FIGHT))
                            self.startup_party_elements(_name)
                            _model[PartyKey.KEY_STATE] = PartyState.STATE_READY_TO_FIGHT
                            _model[PartyKey.KEY_TIME_LEFT] = PartyConst.TIME_MAX_READY
                    elif _state == PartyState.STATE_READY_TO_FIGHT:
                        if _model[PartyKey.KEY_TIME_LEFT] <= 0:
                            print('> Party [{}] change state to [{}]'.format(_name, PartyState.STATE_IN_PROGRESS))
                            _model[PartyKey.KEY_STATE] = PartyState.STATE_IN_PROGRESS
                            _model[PartyKey.KEY_TIME_LEFT] = PartyConst.TIME_MAX_GAME
                    elif _state == PartyState.STATE_IN_PROGRESS:
                        if sum([int(_mob.is_alive) for _mob in _model[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS]]) <= 1:
                            print('> Party [{}] change state to [{}]'.format(_name, PartyState.STATE_WINNER))
                            for _mob in _model[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS]:
                                if _mob.is_alive:
                                    _model[PartyKey.KEY_DEAD_POOL].append(_mob.name)
                                    break
                            _model[PartyKey.KEY_STATE] = PartyState.STATE_WINNER
                            _model[PartyKey.KEY_TIME_LEFT] = PartyConst.TIME_MAX_WIN
                            _has_winner = False
                            for _mob in _model[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS]:
                                if _mob.is_alive:
                                    _has_winner = True
                                    print('> Party [{}] Winner is: [{}]'.format(_name, _mob.name))
                                    break
                            if not _has_winner:
                                print('> Party [{}] NO WINNER !')
                    _model[PartyKey.KEY_PREV_STATE] = _state

                    # ***** Delete dead mobs
                    _bolt_temp = list()
                    for _bolt in _model[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_BOLTS]:
                        if _bolt.is_alive:
                            _bolt_temp.append(_bolt)

                    _asteroid_temp = list()
                    for _asteroid in _model[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS]:
                        if not -PartyConst.WIDTH < _asteroid.x < PartyConst.WIDTH:
                            continue
                        if not -PartyConst.HEIGHT < _asteroid.y < PartyConst.HEIGHT:
                            continue
                        _asteroid_temp.append(_asteroid)

                    _model[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS] = _asteroid_temp
                    _model[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_BOLTS] = _bolt_temp

                    # ***** Delete party
                    if _state == PartyState.STATE_PARTY_ENDED:
                        self.delete_party(_name)
                QThread.currentThread().msleep(int(SERVICE_STATE_PERIOD_S * 1000))

            except Exception as e:
                print('> [ERR] {} > {}: {}'.format(_service_name, type(e).__name__, e))
        print('> {} ended'.format(_service_name))

    def service_debug(self):
        """ Debug display """
        if not DEBUG_MODE: return

        _service_name = 'Service::Debug'
        print('> {} is running...'.format(_service_name))
        while self.services_are_running:
            try:
                QThread.currentThread().msleep(int(DEBUG_DISPLAY_PERIOD_S * 1000))
            except Exception as e:
                pass
        print('> {} ended'.format(_service_name))

    def start_shoot(self, mob, direction: np.ndarray):
        """  """
        if mob.type == ModelType.SHIP_MODEL:
            _time = time.time()
            if self.core_timers[TimerSettings.KEY_SHOOT].get(mob.name) is None:
                self.core_timers[TimerSettings.KEY_SHOOT][mob.name] = _time
            else:
                if _time - self.core_timers[TimerSettings.KEY_SHOOT][mob.name] > TimerSettings.TIMER_SHOOT_PERIOD_S:
                    self.core_timers[TimerSettings.KEY_SHOOT][mob.name] = _time
                    _bolt = BoltModel(creator=mob.name)
                    _bolt.set_dir(direction)
                    _bolt.set_position(mob.xy + direction * mob.radius)
                    _bolt.set_speed(np.array([1000, 0]))
                    return _bolt
