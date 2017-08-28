import sys
sys.path.append('../')

import IOPM.import_hot as import_hot
import IOPM.import_message as import_message
import time

def main():
    while True:
        import_hot.main()
        import_message.main()
        time.sleep(60)


if __name__ == '__main__':
    main()