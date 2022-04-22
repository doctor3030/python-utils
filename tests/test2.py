import time

for i in range(10):
    try:
        print('Proc A {}'.format(i), flush=True)
        time.sleep(1)
    except KeyboardInterrupt:
        print('Proc A exiting..', flush=True)
