from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout


class MenuView(QWidget):
    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller
        self.buttons = dict()
        self.init()

    def init(self):
        b_list = self.buttons['list'] = QPushButton('List')
        b_create = self.buttons['create'] = QPushButton('Create')
        b_join = self.buttons['join'] = QPushButton('Join')
        b_watch = self.buttons['watch'] = QPushButton('Watch')
        b_quit = self.buttons['quit'] = QPushButton('Quit')

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.buttons['list'])
        main_layout.addWidget(self.buttons['create'])
        main_layout.addWidget(self.buttons['join'])
        main_layout.addWidget(self.buttons['watch'])
        main_layout.addWidget(self.buttons['quit'])
        self.setLayout(main_layout)

        b_quit.pressed.connect(self._quit)
        b_join.pressed.connect(self.controller.callback_join_party)
        b_list.pressed.connect(self.controller.callback_show_party_list)
        b_create.pressed.connect(self.controller.callback_show_party_form)
        b_watch.pressed.connect(self.controller.callback_watch_party)

        for _but in self.buttons.values():
            _but.setFocusPolicy(Qt.NoFocus)

    def _quit(self):
        self.controller.stop()
