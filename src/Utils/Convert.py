
def minutes(_min):
    return _min * 60


def secondes(_sec):
    return _sec


def hsv_to_rgb(hue=0, saturation=1, value=1):
    _H = hue
    _S = saturation
    _V = value

    _C = _S * _V
    _X = _C * (1 - abs((_H/60) % 2 - 1))
    _m = _V - _C

    if 0 <= _H < 60:
        _Rp, _Gp, _Bp = _C, _X, 0
    elif 60 <= _H < 120:
        _Rp, _Gp, _Bp = _X, _C, 0
    elif 120 <= _H < 180:
        _Rp, _Gp, _Bp = 0, _C, _X
    elif 180 <= _H < 240:
        _Rp, _Gp, _Bp = 0, _X, _C
    elif 240 <= _H < 300:
        _Rp, _Gp, _Bp = _X, 0, _C
    else:
        _Rp, _Gp, _Bp = _C, 0, _X
    return (_Rp+_m)*255, (_Gp+_m)*255, (_Bp+_m*255)
