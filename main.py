#!/usr/bin/env python

import argparse
import configparser
import os
from batotodownloader import BatotoDownloader

def setup_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help = 'Url of any page within a chapter')
    parser.add_argument('-o', '--output', help = 'Archive output', default = "/tmp/comics.cbz")
    parser.add_argument('-c', '--chapters', type = int, help = 'How many chapters should be downloaded', default=1)
    parser.add_argument('-i', '--initialchapter', type = int, help = 'Initial number for Chapter sequence', default=1)
    parser.add_argument('-l', '--load', action="store_true", help = 'Use previous option')
    return parser.parse_args()

def merge_arguments(args):
    config_path = os.path.expanduser("~/.mangadl.rc")
    config = configparser.ConfigParser()
    config.read(config_path)

    if 'history' not in config:
        return

    history = config['history']

    if 'lastchapter' in history:
        args.initialchapter = int (history['lastchapter'])

    if 'nexturl' in history:
        args.url = history['nexturl']

    if 'chapters' in history:
        args.chapters = history['chapters']

    return args

if __name__ == '__main__':
    args = setup_arguments()
    if (args.load):
        args = merge_arguments(args)

    downloader = BatotoDownloader(args.url, args.output, args.chapters, args.initialchapter)
    downloader.download()
