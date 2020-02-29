import time

import numpy as np
import sys

from PySide2.QtCore import QTimer, QPoint, QSize, QRect
from PySide2.QtGui import QPaintEvent, QPainter, QPen, QBrush, QColor, Qt, QMouseEvent, \
    QCursor, QPixmap, QPainterPath, QFont, QKeyEvent, QTransform
from PySide2.QtWidgets import QWidget, QApplication, QSizePolicy

from Model.PartyModel import PartyConst
from Model.ShipModel import ShipModel
from Model.ModelType import ModelType
from View.Painter.AsteroidPainter import AsteroidPainter
from View.Painter.BackgroundPainter import BackgroundPainter
from View.Painter.BasePainter import BasePainter
from View.Painter.BoltPainter import BoltPainter
from View.Painter.ShipPainter import ShipPainter


class GameBoardView(QWidget):
    def __init__(self, controller=None):
        QWidget.__init__(self)
        self.controller = controller

        # Camera settings
        self.camera_pst = None
        self.anchor_pst = None
        self.camera_increment = 0
        self.camera_is_locked = True

        self.camera_mode = 1

        self.debug_rot = 0
        self.my_painters = None

        self.init()

    def init(self):
        self._init_window()
        self._init_env()
        self._init_models()
        self._init_painters()

    def _init_window(self):
        self.setMinimumSize(1000, 800)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.StrongFocus)

        self.timer_paint_event = QTimer()
        self.timer_paint_event.timeout.connect(self.update)

        self.debug_t = 0

    def start(self):
        self.timer_paint_event.start(20)

    def _init_env(self):
        self.camera_pst = QPoint(self.width()//2, self.height()//2)

    def _init_models(self):
        self.model_ships = [ShipModel(np.array([0, 0]), np.array([0, 1]), np.array([0, 0]))]
        BasePainter().set_transform(self.transform_world_to_screen)

    def _init_painters(self):
        self.my_painters = dict()
        self.my_painters[ModelType.SHIP_MODEL] = ShipPainter(self)
        self.my_painters[ModelType.BOLT_MODEL] = BoltPainter(self)
        self.my_painters['background'] = BackgroundPainter(self)
        self.my_painters['asteroid'] = AsteroidPainter(self)
        self.update()

    def paintEvent(self, event: QPaintEvent):
        self.debug_t += 1
        painter = QPainter(self)
        _cam_mode = self.camera_mode % 3
        if _cam_mode in [0, 1]:
            self.draw_game(painter)

        if _cam_mode in [1]:
            self.draw_mini_map(painter)

        if _cam_mode in [2]:
            self.draw_mini_map(painter, is_full=True)

        painter.end()

    def draw_mini_map(self, painter, is_full=False):
        _pixmap_minimap = QPixmap(QSize(min([self.width(), self.height()]), min([self.width(), self.height()]))) if is_full else QPixmap(QSize(350, 350))
        if is_full:
            _p_origin = QPoint((self.width() - _pixmap_minimap.width())//2, (self.height() - _pixmap_minimap.height())//2)
        else:
            _p_origin = QPoint(self.width() - _pixmap_minimap.width(), self.height() - _pixmap_minimap.height())
        _pixmap_minimap.fill(QColor('#00284d'))

        # DRAW DEAD ZONE
        _dz_radius = self.controller.get_dead_zone_radius()
        _xy = QPoint(*self.controller.get_dead_zone_center().tolist())

        # GET MOBILE OBJECTS
        _model_ships = self.controller.get_data_from_players(enemy_only=False)
        _model_bolts = self.controller.get_data_from_bolts()
        _model_asteroids = self.controller.get_data_from_asteroids()

        # SET MINI MAP
        _w_ratio = _pixmap_minimap.width() / (PartyConst.WIDTH * 1.25)
        _h_ratio = _pixmap_minimap.height() / (PartyConst.HEIGHT * 1.25)

        _minimap_painter = QPainter(_pixmap_minimap)
        _minimap_painter.setOpacity(1)
        for _ship in _model_ships:
            _w = _ship.radius * _w_ratio
            if _w < 3:
                _w = 3
            _x, _y = int(_ship.x * _w_ratio) + _pixmap_minimap.width() // 2, int(_ship.y * _h_ratio) + _pixmap_minimap.height()//2

            if _ship.is_alive:
                _factor_1 = (time.time() * 2) % 2
                _factor_2 = (time.time() * 2 + .5) % 2

                _minimap_painter.setPen(QPen(QColor('#ffffff'), 1, Qt.SolidLine))
                _minimap_painter.setOpacity(1 - _factor_1)
                _minimap_painter.drawEllipse(QPoint(_x, _y), int(20 * _factor_1), int(20 * _factor_1))
                _minimap_painter.setOpacity(1 - _factor_2)
                _minimap_painter.drawEllipse(QPoint(_x, _y), int(20 * _factor_2), int(20 * _factor_2))

            _minimap_painter.setPen(QPen(QColor(*_ship.color), _w, Qt.SolidLine))
            _minimap_painter.setOpacity(1)
            _minimap_painter.drawPoint(_x, _y)

        for _astroid in _model_asteroids:
            _w = _astroid.radius * _w_ratio
            if _w < 5:
                _w = 5
            _pen = QPen(QColor('#ffb86c'), _w, Qt.SolidLine)
            _pen.setCapStyle(Qt.RoundCap)
            _minimap_painter.setPen(_pen)
            _x, _y = int(_astroid.x * _w_ratio) + _pixmap_minimap.width() // 2, int(_astroid.y * _h_ratio) + _pixmap_minimap.height()//2
            _minimap_painter.drawPoint(_x, _y)
        for _bolt in _model_bolts:
            _w = _bolt.radius * _w_ratio
            if _w < 1:
                _w = 1
            _minimap_painter.setPen(QPen(QColor('#ff5555'), _w, Qt.SolidLine))
            _x, _y = int(_bolt.x * _w_ratio) + _pixmap_minimap.width() // 2, int(_bolt.y * _h_ratio) + _pixmap_minimap.height()//2
            _minimap_painter.drawPoint(_x, _y)

        _xy.setX(_xy.x() * _w_ratio + _pixmap_minimap.width() // 2)
        _xy.setY(_xy.y() * _h_ratio + _pixmap_minimap.height() // 2)

        _minimap_painter.setPen(QPen(QColor('#8be9fd'), 3, Qt.SolidLine))
        _minimap_painter.drawEllipse(_xy, _dz_radius * _w_ratio, _dz_radius * _h_ratio)

        if not is_full:
            _minimap_painter.setPen(QPen(QColor('#ffffff'), 1, Qt.SolidLine))
            _x = -self.camera_pst.x() * _w_ratio + _pixmap_minimap.width() // 2
            _y = self.camera_pst.y() * _h_ratio + _pixmap_minimap.height() // 2
            _w = self.width() * _w_ratio
            _h = self.height() * _h_ratio
            _minimap_painter.drawRect(_x, _y - _h, _w, _h)
        _minimap_painter.end()

        _pixmap_minimap = _pixmap_minimap.transformed(QTransform().scale(1, -1))

        painter.setOpacity(1 if is_full else .75)
        painter.drawPixmap(_p_origin, _pixmap_minimap)

    def draw_game(self, painter):
        self.my_painters[ModelType.SHIP_MODEL].setup()
        self.my_painters[ModelType.BOLT_MODEL].setup()
        self.my_painters['background'].setup()

        painter.setBrush(QBrush(QColor('#20124d')))
        painter.drawRect(0, 0, self.width(), self.height())
        try:
            # DRAW BACKGROUND
            painter.setPen(QPen(QBrush(QColor(255, 255, 255)), 2, Qt.SolidLine))
            self.my_painters['background'].paint(painter)

            # DRAW DEAD ZONE
            _dz_radius = self.controller.get_dead_zone_radius()
            _xy = self.controller.get_dead_zone_center().tolist()
            _point_center = self.transform_world_to_screen(*_xy, is_point=True)

            # GET MOBILE OBJECTS
            _model_ships = self.controller.get_data_from_players(enemy_only=False)
            _model_bolts = self.controller.get_data_from_bolts()
            _model_asteroids = self.controller.get_data_from_asteroids()

            # SET CAMERA PSOTOPM
            _ship_to_follow = None
            if self.camera_is_locked:
                _ship_to_follow = self.controller.get_player(self.controller.get_name())
                if _ship_to_follow is not None and _ship_to_follow.is_alive:
                    self.camera_pst = QPoint(-_ship_to_follow.x + self.width() // 2,
                                             _ship_to_follow.y + self.height() // 2)
                elif len(_model_ships):
                    _ship_to_follow = _model_ships[self.camera_increment % len(_model_ships)]
                    self.camera_pst = QPoint(-_ship_to_follow.x + self.width() // 2,
                                             _ship_to_follow.y + self.height() // 2)

            # DRAW MOBILE OBJECTS
            for _mob in _model_bolts + _model_ships + _model_asteroids:
                self.my_painters[_mob.type].paint(painter, model=_mob)

            # DRAW OVERLAY
            _brush_band = QBrush(QColor('#00284d'))
            _barre_height = 100

            _rect_top_title = QRect(0, 0, self.width(), 50)
            _rect_band = QRect(0, (self.height() - _barre_height) // 2, self.width(), _barre_height)
            _rect_text1 = QRect(0, (self.height() - _barre_height) // 2, self.width(), _barre_height // 2)
            _rect_text2 = QRect(0, self.height() // 2, self.width(), _barre_height // 2)
            _rect_board_score_bg = QRect(self.width() // 2 - 250, 50, 500, self.height() - 200)
            _rect_board_title = QRect(0, 100, self.width(), 100)
            _rect_board_score = QRect(0, 200, self.width(), self.height() - 200)
            painter.setPen(QPen(QColor('#ffffff'), 10))
            painter.setFont(QFont('Open Sans', weight=QFont.Bold, pointSize=20))
            if self.controller.is_party_waiting():
                painter.setPen(QPen(Qt.NoPen))
                painter.setBrush(_brush_band)
                painter.setOpacity(.75)
                painter.drawRect(_rect_band)
                painter.setOpacity(1)
                painter.setPen(QPen(QColor('#ffffff'), 50))
                painter.drawText(_rect_text1, Qt.AlignCenter, 'WAITING FOR PLAYERS')
                painter.drawText(_rect_text2, Qt.AlignCenter, '{}'.format(self.controller.get_time_left()))
            elif self.controller.is_party_ready_to_fight():
                painter.setPen(QPen(Qt.NoPen))
                painter.setBrush(_brush_band)
                painter.setOpacity(.75)
                painter.drawRect(_rect_band)
                painter.setOpacity(1)
                painter.setPen(QPen(QColor('#ffffff' if self.controller.get_time_left() > 5 else '#ff5555'), 50))
                painter.drawText(_rect_text1, Qt.AlignCenter, 'READY TO FIGHT?')
                painter.drawText(_rect_text2, Qt.AlignCenter, '{}'.format(self.controller.get_time_left()))
            elif self.controller.has_party_winner():
                painter.setPen(QPen(Qt.NoPen))
                painter.setBrush(_brush_band)
                painter.setOpacity(.75)
                painter.drawRect(_rect_board_score_bg)
                painter.setOpacity(1)
                painter.setPen(QPen(QColor('#ffffff'), 50))
                painter.drawText(_rect_board_title, Qt.AlignHCenter, 'Winner is: {} !'.format(self.controller.get_winner()))
                _text_score = ['=========================',
                               'PARTY: {}'.format(self.controller.get_party_name()),
                               '========= SCORE =========']

                painter.setPen(QPen(QColor('#8be9fd'), 50))
                painter.setFont(QFont('Open Sans', weight=QFont.Bold, pointSize=15))
                for _i, _player in enumerate(self.controller.get_rank_board()[::-1]):
                    _text_score.append('> {: >2}. {: >35}'.format(_i + 1, _player))
                painter.drawText(_rect_board_score, Qt.AlignHCenter, '\n'.join(_text_score))

            elif self.controller.is_party_done():
                painter.drawText(50, 50, 'PARTY DONE !')
            elif self.controller.is_party_in_progress():
                painter.setPen(QPen(Qt.NoPen))
                painter.setBrush(_brush_band)
                painter.setOpacity(.75)
                painter.drawRect(_rect_top_title)
                painter.setOpacity(1)
                painter.setPen(QPen(QColor('#8be9fd'), 50))
                painter.setFont(QFont('Open Sans', weight=QFont.Bold, pointSize=10))
                if _ship_to_follow is not None:
                    painter.drawText(50, 25, 'TimeLeft: {1}     |     Alive: {0}    |    Player: {2}    |'
                                             '    Life: {3}%'.format(sum([_ship.is_alive for _ship in _model_ships]),
                                     self.controller.get_time_left(), _ship_to_follow.name, int(_ship_to_follow.life * 100)))
                else:
                    painter.drawText(50, 25, 'TimeLeft: {1}     |     Alive: {0}'.format(sum([_ship.is_alive for _ship in _model_ships]),
                                                                    self.controller.get_time_left()))
            # DRAW DEAD ZONE FILL
            _path = QPainterPath()
            _path.addRect(QRect(_point_center.x() - PartyConst.WIDTH, _point_center.y() - PartyConst.HEIGHT,
                                PartyConst.WIDTH * 2, PartyConst.HEIGHT * 2))
            _path.addEllipse(_point_center, _dz_radius, _dz_radius)
            painter.setPen(QPen(QColor('#00ffff'), 10, Qt.SolidLine))
            painter.setBrush(QBrush(QColor('#00ffff')))
            painter.setOpacity(.25)
            painter.drawPath(_path)
            painter.setOpacity(1.)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawEllipse(_point_center, _dz_radius, _dz_radius)
            painter.setPen(QPen(QColor('#ffffff'), 5, Qt.SolidLine))
            painter.drawEllipse(_point_center, _dz_radius, _dz_radius)

        except Exception as e:
            print('> [ERR] paintEvent: {}:{}'.format(type(e).__name__, e))

    def transform_world_to_screen(self, x: int, y: int, is_point=False):
        _point = round(x + self.camera_pst.x()), round(-y + self.camera_pst.y())
        if is_point:
            return QPoint(*_point)
        return _point

    def transform_screen_to_world(self, x: int, y: int, is_point=True):
        _point = round(x - self.camera_pst.x()), round(y - self.camera_pst.y())
        if is_point:
            return QPoint(*_point)
        return _point

    def mousePressEvent(self, event: QMouseEvent):
        self.anchor_pst = QCursor.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.camera_is_locked:
            self.camera_pst += QCursor.pos() - self.anchor_pst
            self.anchor_pst = QCursor.pos()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space:
            self.camera_is_locked = not self.camera_is_locked
        elif event.key() == Qt.Key_Left:
            self.camera_increment -= 1
        elif event.key() == Qt.Key_Right:
            self.camera_increment += 1
        elif event.key() == Qt.Key_M:
            self.camera_mode += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = GameBoardView()
    view.show()
    sys.exit(app.exec_())
