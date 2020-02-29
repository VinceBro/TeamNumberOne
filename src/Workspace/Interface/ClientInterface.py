import abc
import sys
from typing import Tuple, List, Union

import numpy as np

from Model.MotionModel import MotionModel
from Model.BaseModel import BaseModel
from Model.ShipModel import ShipModel
from Model.AsteroidModel import AsteroidModel
from Model.BoltModel import BoltModel


class ClientInterface(abc.ABC):
    # --------------- PARTY MOBILE OBJECTS ---------------
    @abc.abstractmethod
    def get_name(self) -> str:
        """
        Get your player name.
        """
        pass

    @abc.abstractmethod
    def get_mobs_in_radius(self, near_point: np.ndarray, radius: int, enemy_only=False) -> List[BaseModel]:
        """
        Return a list of mobile objects near to the point with a radius
        """
        pass

    @abc.abstractmethod
    def get_data_from_players(self, enemy_only=False) -> List[ShipModel]:
        """
        Return a list with the references of all the players (ShipModel)
        """
        pass

    @abc.abstractmethod
    def get_data_from_mobs(self, enemy_only=False) -> List[BaseModel]:
        """
        Return a list with the references of all mobs (ShipModel, AsteroidModel and BoltModel)
        """
        pass

    @abc.abstractmethod
    def get_player(self, name: str) -> ShipModel:
        """
        Return the ship thanks to the player name
        """
        pass

    @abc.abstractmethod
    def get_players_name(self) -> List[str]:
        """
        Return a list with all players name in the party (not observers)
        """
        pass

    @abc.abstractmethod
    def get_data_from_asteroids(self) -> List[AsteroidModel]:
        """
        Return a list with the references of all asteroids (AsteroidModel)
        """
        pass

    @abc.abstractmethod
    def get_asteroid(self, name: str) -> AsteroidModel:
        """
        Return the asteroid thanks to the asteroid name
        """
        pass

    @abc.abstractmethod
    def get_data_from_bolts(self) -> List[BoltModel]:
        """
        Return a list with the references of all bolts (BoltModel)
        """
        pass

    # --------------- PLAYER MOTION ---------------
    @abc.abstractmethod
    def set_motion_command(self, motion: MotionModel) -> None:
        """
        Set the motion command of your ship to the server
        """
        pass

    @abc.abstractmethod
    def get_motion_from_party(self) -> List[MotionModel]:
        """
        Get the motion command of all players in the party
        """
        pass

    # --------------- PARTY MODEL ---------------
    @abc.abstractmethod
    def wait_until_event(self) -> bool:
        """
        Wait until a network package is received. This package update the party model.
        > A 1.0 second timeout is set. If the time is out return false, otherwise return true.
        """
        pass

    @abc.abstractmethod
    def get_time_left(self) -> int:
        """
        Get the time left of the party before another state
        """
        pass

    @abc.abstractmethod
    def get_dead_zone_radius(self) -> float:
        """
        Get the dead zone radius
        """
        pass

    @abc.abstractmethod
    def get_dead_zone_center(self) -> np.ndarray:
        """
        Get the dead zone center
        """
        pass

    @abc.abstractmethod
    def get_winner(self) -> str:
        """
        Get the player that win the party
        """
        pass

    @abc.abstractmethod
    def get_rank_board(self) -> List[str]:
        """
        Get the rank board at the end of the party
        """
        pass

    # --------------- PARTY STATES ---------------
    @abc.abstractmethod
    def is_party_done(self) -> bool:
        """
        Check if the party is done
        """
        pass

    @abc.abstractmethod
    def is_party_waiting(self) -> bool:
        """
        Check if the party is already waiting for players
        """
        pass

    @abc.abstractmethod
    def is_party_ready_to_fight(self) -> bool:
        """
        Check if the players are ready to fight
        """
        pass

    @abc.abstractmethod
    def is_party_in_progress(self) -> bool:
        """
        Check if the party is running
        """
        pass

    @abc.abstractmethod
    def has_party_winner(self) -> bool:
        """
        Check if the party has a winner
        """
        pass

    @abc.abstractmethod
    def is_spectator(self) -> bool:
        """
        Check if the current client is a spectator or not
        """

    # --------------- STATIC METHOD ---------------
    @staticmethod
    def get_the_nearest_mob(point: np.ndarray, mob_list: List[BaseModel]) -> Tuple[float, Union[BaseModel, None]]:
        """
        Get the nearest object from a point with an object list.
        :param point: An 2 dimensions array for th position (example: np.array([0, 0])
        :param mob_list: A list of BaseModel (Asteroid, ShipModel or BoltModel)
        :return: Tuple with a distance and the nearest BaseModel
        """
        try:
            return min([(np.linalg.norm(_mob.xy - point), _mob) for _mob in mob_list], key=lambda x: x[0])
        except ValueError as _:
            return 0., None

    @staticmethod
    def get_mobs_inside_area(point: np.ndarray, radius: float, mob_list: List[BaseModel],
                             exclude: Union[str, None]=None) -> List[Tuple[float, BaseModel]]:
        """
        # TODO Make documentation
        Get mobile objects inside a circle.
        :param point:
        :param radius:
        :param mob_list:
        :param exclude:
        :return:
        """
        try:
            # Filter
            _mob_list = []
            if exclude is not None:
                for _mob in mob_list:
                    if _mob.name == exclude or _mob.creator == exclude:
                        continue
                    _mob_list.append(_mob)
            else:
                _mob_list = mob_list
            return sorted([(np.linalg.norm(_mob.xy - point), _mob) for _mob in _mob_list if np.linalg.norm(_mob.xy - point) < radius], key=lambda x: x[0])
        except ValueError as _:
            return []


    @staticmethod
    def get_distance_between(mob1: BaseModel, mob2: BaseModel) -> float:
        """
        Get distance between two mobs.
        :param mob1: first mob (AsteroidModel, ShipModel and BoltModel)
        :param mob2: second mob (AsteroidModel, ShipModel and BoltModel)
        :return: distance with floating format
        """
        return np.linalg.norm(mob1.xy - mob2.xy)

    @staticmethod
    def get_direction_vector(xy: np.ndarray) -> np.ndarray:
        """
        Get a direction vector normalized [x, y] from a vector.
        :param xy: A numpy array with two dimensions
        :return: A numpy array with two dimensions normalized
        """
        _dist = np.linalg.norm(xy)
        if _dist > 0:
            return xy / _dist
        else:
            print('> [WARN] You cannot get a direction vector from a null vector.', file=sys.stderr)
            return xy

    @staticmethod
    def get_direction_between(origin_mob: BaseModel, target_mob: BaseModel) -> np.ndarray:
        """
        Get a direction vector from a mob to another.
        :param origin_mob: A BaseModel object for the origin
        :param target_mob: A BaseModel object for the target
        :return: A numpy array with two dimensions normalized
        """
        return ClientInterface.get_direction_vector(target_mob.xy - origin_mob.xy)

    @staticmethod
    def get_middle_point_between(origin_mob: BaseModel, target_mob: BaseModel) -> np.ndarray:
        """
        Get the point between the two mobile objects.
        :param origin_mob: First BaseModel object
        :param target_mob: Second BaseModel object
        :return: A numpy array with two dimensions [X, Y]
        """
        _dist = ClientInterface.get_distance_between(origin_mob, target_mob) // 2
        _direction = ClientInterface.get_direction_between(origin_mob, target_mob)
        return origin_mob.xy + _direction * _dist
