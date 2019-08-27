#!/usr/local/bin/python3
import os
import time

time_now = lambda: time.strftime('%Y_%m_%d_%H_%M_%S')


def event_signal_weak(status: bool, status_prev: bool = None, **env):
    # TODO: something you want to do.
    print(time_now(), 'from "%s" to "%s"' % (status_prev, status))


def event_connect_status_changed(status: bool, status_prev: bool = None, **env):
    # TODO: something you want to do.
    print(time_now(), 'from "%s" to "%s"' % (status_prev, status))


def event_lock_status_changed(status: bool, status_prev: bool = None, **env):
    # TODO: something you want to do.
    print(time_now(), 'from "%s" to "%s"' % (status_prev, status))


if __name__ == '__main__':
    import sys
    import json

    from_json = lambda x: json.loads(x)

    env = os.environ
    if len(sys.argv) >= 2:
        event = sys.argv[1]
        events = {
            'weak': event_signal_weak,
            'connect': event_connect_status_changed,
            'lock': event_lock_status_changed,
        }

        if event in events:
            events[event](**from_json(env.pop('UNLOCKERX_ENV')), **env)
        else:
            print("Can't execute valid function: %s" % event)
    else:
        print('Must add one event arg.')
