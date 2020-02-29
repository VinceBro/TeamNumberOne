from PySide2.QtWidgets import QWidget, QHBoxLayout, QTableWidget, QTableWidgetItem, QAbstractItemView


class ListPartyView(QWidget):
    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller

        self.view_table = QTableWidget(0, 3)

        self.init()
        self.update_list()

    def init(self):
        # LAYOUT
        layout = QHBoxLayout()
        layout.addWidget(self.view_table)
        self.setLayout(layout)
        self.setMinimumWidth(500)

        # VIEW EVENT
        self.view_table.mouseDoubleClickEvent = self.callback_double_click

        # VIEW SELECTION MODE
        self.view_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.view_table.setSortingEnabled(True)

        # VIEW COSMETIC
        # > Column format
        for _i, _label in enumerate(['Name', 'Number', 'Creator']):
            self.view_table.setHorizontalHeaderItem(_i, QTableWidgetItem(_label))
        self.view_table.horizontalHeader().setStretchLastSection(True)
        self.header_min_size = 100

        # > Row format
        self.view_table.verticalHeader().setVisible(False)

    def update_list(self):
        parties_model = self.controller.get_parties_from_server()
        self.view_table.setRowCount(len(parties_model))
        for _i, _party_model in enumerate(parties_model):
            for _j, _label in enumerate(_party_model):
                self.view_table.setItem(_i, _j, QTableWidgetItem(str(_label)))

    def resizeEvent(self, event):
        for _i in range(self.view_table.columnCount()):
            if not _i:
                self.view_table.setColumnWidth(_i, self.width() - self.header_min_size * (self.view_table.columnCount() - 1))
            else:
                self.view_table.setColumnWidth(_i, self.header_min_size)

    def get_selected(self):
        _row_selection = self.view_table.selectedItems()
        _party_name = None
        if len(_row_selection):
            _party_name = _row_selection[0].text()
        return _party_name

    def callback_double_click(self, event):
        if self.view_table.selectedItems():
            self.controller.callback_join_party()
