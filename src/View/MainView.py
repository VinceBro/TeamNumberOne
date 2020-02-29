from PySide2.QtWidgets import QWidget, QHBoxLayout, QMessageBox, QLabel, QSpinBox, QLineEdit

import Utils.Miscellaneous as Miscellaneous
from View.GameBoardView import GameBoardView
from View.ListPartyView import ListPartyView
from View.MenuView import MenuView


class MainView(QWidget):
    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller
        self.menu_view = MenuView(controller)
        self.list_party_view = ListPartyView(controller)
        self.game_view = GameBoardView(controller)

        self.create_party_widgets = list()

        self.init()

    def init(self):
        self.game_view.hide()
        self.menu_view.show()
        self.list_party_view.hide()
        self._init_win()

    def _init_win(self):
        self.setWindowTitle('Starship BattleRoyal')
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.menu_view)
        main_layout.addWidget(self.list_party_view)
        main_layout.addWidget(self.game_view)
        self.setLayout(main_layout)

        self.menu_view.setFixedSize(350, 500)

    def show_parties_list(self):
        self.list_party_view.update_list()
        self.list_party_view.show()
        self.menu_view.show()
        self.game_view.hide()

    def show_playing_mode(self):
        self.list_party_view.hide()
        self.menu_view.hide()
        self.game_view.show()

    def show_party_form(self):
        party_form = QMessageBox()
        party_form.setWindowTitle('Create a network party')
        _label_name = QLabel('Name:')
        _label_limit = QLabel('Limit of players:')
        _edit_name = QLineEdit()
        _edit_name.setText(Miscellaneous.get_random_word())
        _spinbox_limit = QSpinBox()
        _spinbox_limit.setMaximum(10)
        _spinbox_limit.setMinimum(1)
        _spinbox_limit.setValue(2)
        create_party_widgets = [_label_name, _edit_name, _label_limit, _spinbox_limit]
        for widget in create_party_widgets:
            party_form.layout().addWidget(widget)
        party_form.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
        ret = party_form.exec_()
        if ret == QMessageBox.Save:
            _party_model = _edit_name.text(), int(_spinbox_limit.text()), self.controller.get_name()
            self.controller.create_party(_party_model)

    def start(self):
        self.game_view.start()
        self.show()

    def get_party_selected(self):
        return self.list_party_view.get_selected()

    def closeEvent(self, event):
        self.controller.stop()

    def stop(self):
        self.controller.stop()

