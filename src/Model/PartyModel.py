import numpy as np
import time

from Model.ModelType import ModelType as mode_t
from Model.MotionModel import MotionModel
from Model.ShipModel import ShipModel
from Model.AsteroidModel import AsteroidModel
from Model.BoltModel import BoltModel
from Utils.Convert import secondes, minutes


class PartyState:
    STATE_READY_TO_FIGHT = 'ready'
    STATE_INIT = 'party_init'
    STATE_WAITING_FOR_PLAYERS = 'wait_players'
    STATE_IN_PROGRESS = 'in_progress'
    STATE_WINNER = 'winner'
    STATE_PARTY_ENDED = 'party_ended'


class PartyConst:
    # TIMING
    TIME_MAX_WAITING = minutes(1) + secondes(30)
    TIME_MAX_READY = secondes(2)
    TIME_MAX_GAME = minutes(3)
    TIME_MAX_DEAD_ZONE = minutes(2) + secondes(30)
    # TIME_MAX_GAME = secondes(30)
    TIME_MAX_WIN = secondes(10)

    # DEAD ZONE
    WIDTH = 5000
    HEIGHT = 5000
    DEAD_ZONE_MAX_RADIUS = int(((WIDTH ** 2 + HEIGHT ** 2) ** .5) / 2)
    DEAD_ZONE_DAMAGE_PER_S = .2

    # ASTEROID
    ASTEROID_COUNT = 45
    ASTEROID_SPEED_LIMIT = (150, 250)
    ASTEROID_SIZE_LIMIT = (25, 200)
    ASTEROID_RADIUS_SPAWN = 5000

    # MOTION SPECIFICATION (PIXELS PER SEC)
    MOTION_MAX_PROPULSION_ACCEL = 5.
    MOTION_MAX_ROTATION_ACCEL = np.pi
    MOTION_MAX_PROPULSION_SPEED = 500.
    MOTION_MIN_PROPULSION_SPEED = 0.
    MOTION_MAX_ROTATION_SPEED = 2. * np.pi
    MOTION_MIN_ROTATION_SPEED = -2. * np.pi


class PartyKey:
    KEY_DEAD_POOL = 'k_dead_pool'
    KEY_MOB_BOLTS = 'k_mob_bolt'
    KEY_MOB_ASTEROIDS = 'k_mob_ast'
    KEY_MOB_PLAYERS = 'k_mob_plr'
    KEY_DEAD_ZONE_CENTER = 'k_dz_xy'
    KEY_DEAD_ZONE_RADIUS = 'k_dz_r'
    KEY_DEAD_ZONE = 'k_dz'
    KEY_LIMIT = 'k_limit'
    KEY_PLAYERS = 'k_players'
    KEY_PLAYER_CMD = 'k_player_cmd'
    KEY_MOBS = 'k_mobs'
    KEY_CREATED = 'k_created'
    KEY_CREATOR = 'k_creator'
    KEY_STATE = 'k_state'
    KEY_PREV_STATE = 'k_prev_state'
    KEY_TIME_LEFT = 'k_time_left'
    KEY_NAME = 'k_name'
    KEY_MOTION = 'k_motion'


mob_factory = {mode_t.SHIP_MODEL: ShipModel,
               mode_t.ASTEROID_MODEL: AsteroidModel,
               mode_t.BOLT_MODEL: BoltModel,
               }


class PartyModel:
    def __init__(self, name, limit=-1):
        self.name = name
        self.limit = limit
        self.time_left = None
        self.state = PartyState.STATE_INIT
        self.m_players = dict()
        self.m_asteroids = dict()
        self.m_bolts = list()
        self.motions = dict()
        self.dz_radius = PartyConst.DEAD_ZONE_MAX_RADIUS
        self.dz_center = np.array([0, 0])
        self.dead_pool = list()

    def update(self, data):
        self.time_left = data[PartyKey.KEY_TIME_LEFT]
        self.state = data[PartyKey.KEY_STATE]
        self.limit = data[PartyKey.KEY_LIMIT]

        _players = dict()
        _asteroids = dict()
        _bolts = list()

        for _m_player in data[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_PLAYERS]:
            _name = _m_player[mode_t.KEY_NAME]
            if self.m_players.get(_name) is not None:
                _players[_name] = self.m_players[_name].from_dict(_m_player)
            else:
                _players[_name] = ShipModel().from_dict(_m_player)

        for _m_asteroid in data[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_ASTEROIDS]:
            _name = _m_asteroid[mode_t.KEY_NAME]
            if self.m_asteroids.get(_name) is not None:
                _asteroids[_name] = self.m_asteroids[_name].from_dict(_m_asteroid)
            else:
                _asteroids[_name] = AsteroidModel().from_dict(_m_asteroid)

        for _m_bolt in data[PartyKey.KEY_MOBS][PartyKey.KEY_MOB_BOLTS]:
            _bolts.append(BoltModel().from_dict(_m_bolt))

        self.m_bolts = _bolts
        self.m_asteroids = _asteroids
        self.m_players = _players

        self.dead_pool = data[PartyKey.KEY_DEAD_POOL]

        _motions = dict()
        for _name, _motion_dict in data[PartyKey.KEY_MOTION].items():
            _motions[_name] = MotionModel().from_dict(_motion_dict)
        self.motions = _motions

        self.dz_radius = data[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_RADIUS]
        self.dz_center = np.array(data[PartyKey.KEY_DEAD_ZONE][PartyKey.KEY_DEAD_ZONE_CENTER])

    def get_asteroid(self, name: str):
        return self.m_asteroids.get(name)

    def get_player(self, name: str):
        return self.m_players.get(name)

    def get_players_name(self):
        return list(self.m_players.keys())

    def get_asteroids_iterator(self):
        return list(self.m_asteroids.values())

    def get_players_iterator(self):
        return [_player for _player in self.m_players.values()]

    def get_bolts_iterator(self):
        return [_bolt for _bolt in self.m_bolts if _bolt.is_alive]

    def is_done(self):
        return self.state == PartyState.STATE_PARTY_ENDED

    def has_began(self):
        return not self.is_done()

    def get_time_left(self):
        return self.time_left

    def get_dead_zone_radius(self):
        return self.dz_radius

    def get_dead_zone_center(self):
        return self.dz_center

    def __str__(self):
        return '[PARTY]{}({}/{}) | state: {}'.format(
                self.name, len(self.m_players), self.limit, self.state
                )

    @staticmethod
    def get_ended_pkg(party_name, player):
        _radius_dead_zone = (PartyConst.WIDTH**2 + PartyConst.HEIGHT**2)**.5
        return {PartyKey.KEY_LIMIT: 0, PartyKey.KEY_PLAYERS: dict(),
                PartyKey.KEY_MOBS: {PartyKey.KEY_MOB_PLAYERS: list(),
                                    PartyKey.KEY_MOB_ASTEROIDS: list(),
                                    PartyKey.KEY_MOB_BOLTS: list()},
                PartyKey.KEY_CREATED: time.time(),
                PartyKey.KEY_CREATOR: player,
                PartyKey.KEY_STATE: PartyState.STATE_WAITING_FOR_PLAYERS,
                PartyKey.KEY_PREV_STATE: PartyState.STATE_INIT,
                PartyKey.KEY_TIME_LEFT: PartyConst.TIME_MAX_WAITING,
                PartyKey.KEY_NAME: party_name,
                PartyKey.KEY_MOTION: dict(),
                PartyKey.KEY_DEAD_POOL: list(),
                PartyKey.KEY_DEAD_ZONE: {PartyKey.KEY_DEAD_ZONE_RADIUS: _radius_dead_zone,
                                         PartyKey.KEY_DEAD_ZONE_CENTER: np.array([0, 0])},
             }

    def get_mobs_iterator(self):
        return self.get_players_iterator() + self.get_bolts_iterator() + self.get_asteroids_iterator()
