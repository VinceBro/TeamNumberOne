import abc

from PySide2.QtCore import QThread

from Workspace.Interface.ClientInterface import ClientInterface


class BaseWorkspace(QThread):
    def __init__(self, controller):
        QThread.__init__(self)
        self.ctrl: ClientInterface = controller
        self._is_running = False

    @property
    def is_running(self):
        return self._is_running

    def stop(self):
        self._is_running = False

    def run(self):
        assert self.ctrl is not None, 'You must set a controller'
        self._is_running = True
        while self.is_running:
            if not self.ctrl.is_spectator() and self.ctrl.is_party_in_progress():
                self.loop()
            else:
                self.msleep(1000)

    @abc.abstractmethod
    def loop(self):
        pass
