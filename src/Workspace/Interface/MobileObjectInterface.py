import abc
import numpy as np


class MobileObjectInterface(abc.ABC):
    """
    This interface is common to all mobile objects (ShipModel, AsteroidModel and BoltModel).
    > NOTE: These methods are the most important for your artificial intelligence program.
    """

    @abc.abstractmethod
    def life(self) -> float:
        """
        Return the remaining life points of the current mobile object.
        > Example: _life = mob.life
        """
        pass

    @abc.abstractmethod
    def is_alive(self) -> bool:
        """
        Return if the current mobile object is alive or not.
        > Example: _is_alive = mob.is_alive
        """
        pass

    @abc.abstractmethod
    def radius(self) -> int:
        """
        Return the radius of the current mobile object.
        > Example: _radius = mob.radius
        """
        pass

    @abc.abstractmethod
    def x(self) -> float:
        """
        Return the X position of the current mobile object.
        > Example: _x = mob.x
        """
        pass

    @abc.abstractmethod
    def y(self) -> float:
        """
        Return the Y position of the current mobile object.
        > Example: _y = mob.y
        """
        pass

    @abc.abstractmethod
    def position(self) -> np.ndarray:
        """
        Return the (X, Y) position of the current mobile object.
        > Example: _xy = mob.position
        """
        pass

    @abc.abstractmethod
    def xy(self) -> np.ndarray:
        """
        Return the (X, Y) position of the current mobile object.
        > Example: _xy = mob.xy
        """
        pass

    @abc.abstractmethod
    def dir(self) -> np.ndarray:
        """
        Return the direction of the current mobile object with a 2D vector.
        > Example: _dir = mob.dir
        """
        pass

    @abc.abstractmethod
    def angle(self) -> float:
        """
        Return the direction of the current mobile object in degree.
        > Example: _angle = mob.degree
        """
        pass

    @abc.abstractmethod
    def dir_x(self) -> float:
        """
        Return the direction (2D vector) in X of the current mobile object.
        > Example: _dir_x = mob.dir_x
        """
        pass

    @abc.abstractmethod
    def dir_y(self) -> float:
        """
        Return the direction (2D vector) in Y of the current mobile object.
        > Example: _dir_xy = mob.dir_y
        """
        pass

    @abc.abstractmethod
    def get_propulsion_speed(self) -> float:
        """
        Get the propulsion speed of the current mobile object.
        > Example: _speed = mob.get_propulsion_speed()
        """
        pass

    @abc.abstractmethod
    def get_rotation_speed(self) -> float:
        """
        Get the rotation speed of the current mobile object.
        > Example: _rotation_speed = mob.get_rotation_speed()
        """
        pass
