import sys


def LogError(func):
    def logWrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print('> [ERR] {}: [{}] {}'.format(func.__name__, type(e).__name__, e), file=sys.stderr)
    return logWrapper
