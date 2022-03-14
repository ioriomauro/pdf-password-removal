# -*- coding: utf-8 -*-
import argparse
import getpass
import logging
import os
import sys
import warnings

import pikepdf


logger = logging.getLogger('main')


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
        'pdfnames', nargs='+', help='File name to unprotect')

    return parser


def get_nopwd_name(filename):
    dirname, basename = os.path.split(filename)
    name, ext = os.path.splitext(basename)
    return os.path.join(dirname, f'{name}-nopwd{ext}')


def main(opts):
    passwd = ''
    if len(opts.pdfnames) <= 1:
        opts.batch = False

    warnings.filterwarnings('error', category=UserWarning, module='pikepdf')

    for name in opts.pdfnames:
        if not os.path.exists(name):
            logger.warning('File not found: %r', name)
            if not opts.batch:
                logger.error('Exiting on FileNotFound error (non-batch)')
                return 2
        while True:
            try:
                pdf = pikepdf.open(name, password=passwd)
                if not passwd:
                    raise SystemError(
                        'No password was needed to open this PDF.')
                newname = get_nopwd_name(name)
                pdf.save(newname)
                logger.info('Saved %r', newname)
                break
            except SystemError as e:
                msg = getattr(e, '__cause__', str(e))
                logger.info('Skipping %r: %s', name, msg)
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
