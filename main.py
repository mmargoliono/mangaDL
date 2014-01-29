#!/usr/bin/env python

import argparse
from batotodownloader import BatotoDownloader

def setup_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help = 'Url of any page within a chapter')
    parser.add_argument('-o', '--output', help = 'Archive output', default = "/tmp/comics.cbz")
    parser.add_argument('-c', '--chapters', type = int, help = 'How many chapters should be downloaded', default=1)
    parser.add_argument('-i', '--initialchapter', type = int, help = 'Initial number for Chapter sequence', default=1)
    return parser.parse_args()

if __name__ == '__main__':
    args = setup_arguments()
    downloader = BatotoDownloader(args.url, args.output, args.chapters, args.initialchapter)
    downloader.download()
