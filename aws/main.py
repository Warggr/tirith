#!/bin/python3

import json
import sys
import os
from amazon_manager import AmazonManager

if __name__ == '__main__':
    manager = AmazonManager()
    if len(sys.argv) != 3:
        try:
            manager.create()
            print(f'Your load balancer is deployed at {manager.load_balancer.dns_name}.')
            i = input('Press ENTER to quit.')
        finally:
            manager.delete()
    else:
        if sys.argv[1] not in ['stop', 'start', 'create', 'delete', 'more', 'less', 'fill', 'switch']:
            print(f'Usage: {sys.argv[0]} [create|delete|stop|start] filename')
        else:
            if sys.argv[1] == 'create':
                with open(sys.argv[2], 'x') as file:
                    manager.create()
                    print('DNS_NAME:', manager.load_balancer.dns_name)
                    json.dump(manager.serialize(), file)
            else:
                with open(sys.argv[2], 'r') as file:
                    manager.unserialize(json.load(file))

                if sys.argv[1] == 'delete':
                    manager.delete()
                    os.remove(sys.argv[2])

                else:
                    if sys.argv[1] == 'stop':
                        manager.stop()
                    elif sys.argv[1] == 'start':
                        manager.restart()
                        print('DNS_NAME:', manager.load_balancer.dns_name)
                    elif sys.argv[1] == 'more':
                        manager.more()
                    elif sys.argv[1] == 'less':
                        manager.less()
                    elif sys.argv[1] == 'fill':
                        manager.fill()
                    elif sys.argv[1] == 'switch':
                        manager.switch()

                    with open(sys.argv[2], 'w') as file:
                        json.dump(manager.serialize(), file)
