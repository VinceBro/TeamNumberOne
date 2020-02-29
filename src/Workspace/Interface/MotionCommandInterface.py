import abc
import numpy as np


class MotionCommandInterface(abc.ABC):
    @abc.abstractmethod
    def acceleration(self) -> float:
        """
        Get the acceleration (percentage) of your motion command.
        > Example: _acceleration = motion.acceleration
        """
        pass

    @abc.abstractmethod
    def rotation(self) -> float:
        """
        Get the rotation (percentage) for your motion command.
        > Example: _rotation = motion.rotation
        """
        pass

    @abc.abstractmethod
    def set_rotation(self, percent: float) -> None:
        """
        Set the rotation (percentage) from -1.0 to 1.0 to your ship. The server applies it to the current orientation.
        > NOTE: -1.0 turns the ship to the left and +1.0 turns the ship to the right.
        > Example: motion.set_rotation( 1.0 )
        """
        pass

    @abc.abstractmethod
    def set_acceleration(self, percent: float) -> None:
        """
        Set the acceleration speed from -1.0 to 1.0 to your ship. The server applies it to the current speed.
        > Example: motion.set_acceleration( -1.0 )
        """
        pass

    @abc.abstractmethod
    def shoot(self) -> None:
        """
        Set the ship state to SHOOT. The server shoot to the shooting direction and ignore your motion command.
        > Example: motion.shoot()
        """
        pass

    @abc.abstractmethod
    def move(self) -> None:
        """
        Set the ship state to MOVE. The server just applies your speed and rotation command to your ship.
        > Example: motion.move()
        """
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """
        Set the ship state to STOP. The server reduces speed and rotation to stop your ship.
        > Example: motion.stop()
        """
        pass

    @abc.abstractmethod
    def set_shoot_dir(self, shoot_dir: np.ndarray) -> None:
        """
        Set the shoot direction with a 2D vector.
        > Example: Shoot to the top (90 degrees) is np.array([1, 0]).
        > Example: motion.set_shoot_dir( np.array( [1, 0] ) )
        """
        pass
