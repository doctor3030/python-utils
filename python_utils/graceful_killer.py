# import signal
# import time
import enum


class KillMethods(enum.Enum):
    CLOSE = 'close'
    KILL_FLAG = 'kill_flag'


class GracefulKiller:
    objs = None
    method = KillMethods.CLOSE

    def exit_gracefully(self, *args):
        if self.objs:
            for obj in self.objs:
                if self.method == KillMethods.CLOSE:
                    obj.close()
                elif self.method == KillMethods.KILL_FLAG:
                    obj.KILL_FLAG = True
