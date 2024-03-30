#!/usr/bin/env python3

import argparse
import urllib.request

import portend


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    portend.occupied(args.host, args.port, timeout=3)
    root = 'http://{host}:{port}/'.format(**vars(args))
    urllib.request.urlopen(root)


__name__ == '__main__' and run()
