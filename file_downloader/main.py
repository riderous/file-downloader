import argparse
import datetime
import logging
import os

from . import downloader

logger = logging.getLogger(__name__)


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
    level = logging.INFO
    if args.quiet:
        level = logging.ERROR
    elif args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level, format='- %(message)s')


def main():
    args = parse_args()
    configure_logging(args)
    start_time = datetime.datetime.now()
    try:
        downloader.AsyncIODownloader(args.file.name, args.destination).run()
        logger.info("Done. Took %s", datetime.datetime.now() - start_time)
    except Exception as why:
        logger.error("Unexpected error: %s", why)
