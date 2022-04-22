import sys
import time

for i in range(10):
    try:
        print('Proc B {}'.format(i), flush=True)
        time.sleep(1)
        #     raise Exception('some exception {}'.format(i))
    except KeyboardInterrupt:
        print('Proc B exiting..', flush=True)
    #     continue
