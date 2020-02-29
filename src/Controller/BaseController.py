import abc


class BaseController(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def set_connexion_info(self, host: str, port: int):
        pass

    @abc.abstractmethod
    def join(self):
        pass
