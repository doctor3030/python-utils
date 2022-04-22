import time
import signal
from python_utils.graceful_killer import GracefulKiller, KillMethods


class Test:
    def __init__(self):
        self.stop = False

    def run(self):
        i = 0
        while not self.stop:
            print('Proc C {}'.format(i), flush=True)
            i += 1
            time.sleep(1)

    def close(self):
        print('Proc C exiting..', flush=True)
        self.stop = True


killer = GracefulKiller()
signal.signal(signal.SIGINT, killer.exit_gracefully)
signal.signal(signal.SIGTERM, killer.exit_gracefully)

cls = Test()
killer.objs = [cls]
killer.method = KillMethods.CLOSE

if __name__ == '__main__':
    cls.run()
