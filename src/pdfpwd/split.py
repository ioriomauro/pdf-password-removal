# -*- coding: utf-8 -*-
import argparse
import getpass
import logging
import os
import sys

import pikepdf

from .utils import parse_range_list


logger = logging.getLogger('main')


class ArgTypes:
    @classmethod
    def range(cls, range_list):
        return parse_range_list(range_list)


def get_parser():
    parser = argparse.ArgumentParser(description='')

    parser.add_argument(
        '-v', '--verbose', action='count', default=0, dest='verbosity',
        help='Increase verbosity level by one for every "v" '
            '(default: %(default)s)')
    parser.add_argument(
        '-B', '--no-batch', dest='batch', action='store_false', default=True,
        help='Ask for password for every file name provided '
             '(default: ask once)')
    parser.add_argument(
        '-p', '--pages', dest='pages', type=ArgTypes.range, default=[],
        help='Extract only desired pages. Pages can be specified via '
             'comma-separated numbers or ranges. E.g.: "1,4-5,17-20,23". Page '
             'numbers are 1-based '
             '(default: extract all pages)')
    parser.add_argument(
        'pdfnames', nargs='+', help='File name to split')

    return parser


def split(name, pwd, pages):
    pdf = pikepdf.open(name, password=pwd)
    dirname, basename = os.path.split(name)
    fname, fext = os.path.splitext(basename)
    for p in pages or range(1, len(pdf.pages) + 1):
        s = pikepdf.Pdf.new()
        s.pages.append(pdf.pages[p-1])
        pname = f'{dirname}/{fname}-P{p:02d}{fext}'
        s.save(pname)


def main(opts):
    passwd = ''
    if len(opts.pdfnames) <= 1:
        opts.batch = False

    for name in opts.pdfnames:
        if not os.path.exists(name):
            logger.warning('File not found: %r', name)
            if not opts.batch:
                logger.error('Exiting on FileNotFound error (non-batch)')
                return 2
        while True:
            try:
                split(name, passwd, opts.pages)
                logger.info('Split %r', name)
                break
            except SystemError as e:
                msg = getattr(e, '__cause__')
                if msg is None:
                    msg = str(e)
                logger.warning('Skipping %r: %s', name, msg)
                break
            except pikepdf.PasswordError:
                if passwd == '':
                    if opts.batch:
                        prompt = 'Input PDF password for all files: '
                    else:
                        prompt = f'Input PDF password for {name!r}: '
                else:
                    logger.error('Invalid password for %r', name)
                    return 3
                passwd = getpass.getpass(prompt)


if __name__ == '__main__':
    options = get_parser().parse_args()
    levels = [logging.DEBUG, logging.INFO, logging.WARNING][::-1]
    verbosity = min([options.verbosity, len(levels)-1])
    logging.basicConfig(level=levels[verbosity])
    # if options.verbosity <= len(levels)-1:
    #     for l in ('pikepdf',):
    #         logging.getLogger(l).setLevel(logging.WARNING)
    logger.debug('Starting')
    sys.exit(main(options) or 0)
