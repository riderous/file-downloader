import argparse
import logging
import os

from . import downloader


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download all URLs from the input file")
    parser.add_argument('file', type=argparse.FileType('r'),
                        help="path to the file containing URLs")
    parser.add_argument('-d', '--destination', default='.',
                        type=check_directory,
                        help="directory to put downloaded files")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--quiet', action='store_true',
                       help="suppress output")
    group.add_argument('-v', '--verbose', action='store_true',
                       help='enable some additional debug logging output')
    return parser.parse_args()


def check_directory(value):
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError(
            "directory doesn't exist {}".format(value))
    return value


def configure_logging(args):
    if args.quiet:
        logging.basicConfig(level=logging.ERROR)
    elif args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def main():
    args = parse_args()
    configure_logging(args)
    downloader.Downloader(args.file, args.destination).run()
