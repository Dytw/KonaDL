#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: Konachan Downloader CLI for Linux
Date Created: 13 Apr. 2018
Last Modified: 28 Apr. 2018

Licensed under the GNU General Public License Version 3 (GNU GPL v3),
    available at: https://www.gnu.org/licenses/gpl-3.0.txt
(C) 2018 K4YT3X
"""

from libkonadl import konadl  # Import libkonadl
from libkonadl import print_locker
import argparse
import avalon_framework as avalon
import os
import time
import traceback

VERSION = '1.3.7'


def process_arguments():
    """This function parses all arguments

    Users can customize the behavior of libkonadl using
    commandline arguments
    """
    parser = argparse.ArgumentParser()
    control_group = parser.add_argument_group('Controls')
    control_group.add_argument('-n', '--pages', help='Number of pages to download', type=int, action='store', default=False)
    control_group.add_argument('-a', '--all', help='Download all images', action='store_true', default=False)
    control_group.add_argument('-p', '--page', help='Crawl a specific page', type=int, action='store', default=False)
    control_group.add_argument('-y', '--yandere', help='Crawl Yande.re site', action='store_true', default=False)
    control_group.add_argument('-o', '--storage', help='Storage directory', action='store', default=False)
    control_group.add_argument('--separate', help='Separate images into folders by ratings', action='store_true', default=False)
    control_group.add_argument('-u', '--update', help='Update new images', action='store_true', default=False)
    ratings_group = parser.add_argument_group('Ratings')
    ratings_group.add_argument('-s', '--safe', help='Include Safe rated images', action='store_true', default=False)
    ratings_group.add_argument('-q', '--questionable', help='Include Questionable rated images', action='store_true', default=False)
    ratings_group.add_argument('-e', '--explicit', help='Include Explicit rated images', action='store_true', default=False)
    threading_group = parser.add_argument_group('Threading')
    threading_group.add_argument('-c', '--crawlers', help='Number of post crawler threads', type=int, action='store', default=10)
    threading_group.add_argument('-d', '--downloaders', help='Number of downloader threads', type=int, action='store', default=20)
    etc_group = parser.add_argument_group('Extra')
    etc_group.add_argument('-v', '--version', help='Show KonaDL version and exit', action='store_true', default=False)
    return parser.parse_args()


def check_storage_dir(args):
    """ Processes storage argument and passes it on

    Formats the storage input to the format that libkonadl
    will recognize.
    """
    if args.storage is False:
        return False
    storage = args.storage
    if storage[-1] != '/':
        storage += '/'
    if not os.path.isdir(storage):
        if os.path.isfile(storage) or os.path.islink(storage):
            avalon.error('Storage path specified is a file/link')
        else:
            avalon.warning('Storage directory not found')
            if avalon.ask('Create storage directory?', True):
                try:
                    if not os.mkdir(storage):
                        if args.separate:
                            os.mkdir('{}/safe'.format(storage))
                            os.mkdir('{}/questionable'.format(storage))
                            os.mkdir('{}/explicit'.format(storage))
                        avalon.info('Successfully created storage directory')
                        return storage
                except PermissionError:
                    avalon.error('Insufficient permission to create the specified directory\n')
                    exit(1)
                except Exception:
                    avalon.error('An error occurred while trying to create storage directory\n')
                    traceback.print_exc()
                    exit(0)
            else:
                avalon.error('Storage directory not found')
                avalon.error('Unable to proceed\n')
                exit(1)
    return storage


def display_options(kona, load_progress, args):
    """ Display konadl crawling options

    Prints the options of konadl before start crawling.
    Warns user if questionable images or explicit images
    are to be downloaded.

    Also shows other supplement information if any. More to
    be added in the future.
    """
    avalon.dbgInfo('Program Started')
    avalon.info('Using storage directory: {}{}'.format(avalon.FG.W, kona.storage))
    if load_progress or args.update:
        avalon.info('Sourcing configuration defined in the metadata file')
    else:
        if kona.safe:
            avalon.info('Including {}{}SAFE{}{} rated images'.format(avalon.FG.W, avalon.FM.BD, avalon.FM.RST, avalon.FG.G))
        if kona.questionable:
            avalon.warning('Including {}QUESTIONABLE{} rated images'.format(avalon.FG.W, avalon.FG.Y))
        if kona.explicit:
            avalon.warning('Including {}EXPLICIT{} rated images'.format(avalon.FG.R, avalon.FG.Y))
        if kona.yandere:
            avalon.info('Crawling yande.re')

        if args.pages:
            if args.pages == 1:
                avalon.info('Crawling {}{}{}{}{} Page\n'.format(avalon.FG.W, avalon.FM.BD, args.pages, avalon.FM.RST, avalon.FG.G))
            else:
                avalon.info('Crawling {}{}{}{}{} Pages\n'.format(avalon.FG.W, avalon.FM.BD, args.pages, avalon.FM.RST, avalon.FG.G))
        elif args.all:
            avalon.warning('Crawling {}ALL{} Pages\n'.format(avalon.FG.W, avalon.FG.Y))
        elif args.page:
            avalon.info('Crawling Page #{}'.format(args.page))

    avalon.info('Opening {}{}{}{}{} crawler threads'.format(avalon.FG.W, avalon.FM.BD, args.crawlers, avalon.FM.RST, avalon.FG.G))
    avalon.info('Opening {}{}{}{}{} downloader threads\n'.format(avalon.FG.W, avalon.FM.BD, args.downloaders, avalon.FM.RST, avalon.FG.G))


class konadl_avalon(konadl):
    """ Overwrite original methods for better
    appearance and readability using avalon
    framework.
    """

    @print_locker
    def warn_keyboard_interrupt(self):
        avalon.warning('[Main Thread] KeyboardInterrupt Caught!')
        avalon.warning('[Main Thread] Flushing queues and exiting')

    @print_locker
    def print_saving_progress(self):
        avalon.info('[Main Thread] Saving progress to {}{}{}'.format(avalon.FG.W, avalon.FM.BD, self.storage))

    def print_loading_progress(self):
        avalon.info('[Main Thread] Loading progress from {}{}{}'.format(avalon.FG.W, avalon.FM.BD, self.storage))

    @print_locker
    def print_retrieval(self, url, page):
        avalon.dbgInfo("[Page={}] Retrieving: {}".format(page, url))

    @print_locker
    def print_crawling_page(self, page):
        avalon.info('Crawling page: {}{}#{}'.format(avalon.FM.BD, avalon.FG.W, page))

    @print_locker
    def print_thread_exit(self, name):
        avalon.dbgInfo('[libkonadl] {} thread exiting'.format(name))

    @print_locker
    def print_429(self):
        avalon.error('HTTP Error 429: You are sending too many requests')
        avalon.warning('Trying to recover from error')
        avalon.warning('Putting job back to queue')

    @print_locker
    def print_exception(self):
        avalon.error('An error has occurred in this thread')
        avalon.warning('Trying to recover from error')
        avalon.warning('Putting job back to queue')

    @print_locker
    def print_faulty_progress_file(self):
        avalon.error('Faulty progress file!')
        avalon.error('Aborting\n')


args = process_arguments()

try:
    if __name__ == '__main__':
        kona = konadl_avalon()  # Create crawler object
        kona.icon()

        if args.version:  # prints program legal / dev / version info
            print('CLI Program Version: ' + VERSION)
            print('libkonadl Version: ' + kona.VERSION)
            print('Author: K4YT3X')
            print('License: GNU GPL v3')
            print('Github Page: https://github.com/K4YT3X/KonaDL')
            print('Contact: k4yt3x@protonmail.com\n')
            exit(0)

        kona.storage = check_storage_dir(args)
        if kona.storage is False:
            avalon.error('Please specify storage directory\n')
            exit(1)

        # If progress file exists
        # Ask user if he or she wants to load it
        load_progress = False
        if kona.progress_files_present():
            avalon.info('Progress file found')
            if avalon.ask('Continue from where you left off?', True):
                kona.load_progress = True
                load_progress = True
            else:
                avalon.info('Starting new download progress')
                kona.remove_progress_files()

        # Pass terminal arguments to libkonadl object
        kona.separate = args.separate
        kona.yandere = args.yandere
        kona.safe = args.safe
        kona.questionable = args.questionable
        kona.explicit = args.explicit
        kona.post_crawler_threads_amount = args.crawlers
        kona.downloader_threads_amount = args.downloaders
        display_options(kona, load_progress, args)

        if not kona.safe and not kona.questionable and not kona.explicit and not load_progress and not args.update:
            avalon.error('Please supply information about what you want to download')
            print(avalon.FM.BD + 'You must include one of the following arguments:')
            print('  -s, --safe            Include Safe rated images')
            print('  -q, --questionable    Include Questionable rated images')
            print('  -e, --explicit        Include Explicit rated images')
            print('Use --help for more information\n' + avalon.FM.RST)
            exit(1)
        elif not args.pages and not args.all and not args.page and not load_progress and not args.update:
            avalon.error('Please supply information about what you want to download')
            print(avalon.FM.BD + 'You must include one of the following arguments:')
            print('  -n PAGES, --pages PAGES')
            print('                        Number of pages to download')
            print('  -a, --all             Download all images')
            print('  -p PAGE, --page PAGE  Crawl a specific page')
            print('Use --help for more information\n' + avalon.FM.RST)

        if load_progress:
            kona.crawl()
        elif args.update:
            avalon.info('Updating new images')
            if kona.update() is False:
                avalon.info('{}{}No new images found\n'.format(avalon.FM.BD, avalon.FG.W))
        elif args.pages:
            kona.pages = args.pages
            kona.crawl()
        elif args.all:
            kona.crawl_all_pages()
        elif args.page:
            kona.crawl_page(args.page)

        avalon.info('Main thread exited without errors')
        avalon.info('{}{}{}{}{} image(s) downloaded'.format(avalon.FG.W, avalon.FM.BD, kona.total_downloads, avalon.FM.RST, avalon.FG.G))
        avalon.info('Time taken: {}{}{}{}{} seconds'.format(avalon.FG.W, avalon.FM.BD, round(
            (time.time() - kona.begin_time + kona.time_elapsed), 5), avalon.FM.RST, avalon.FG.G))
        if kona.job_done:
            avalon.info('All downloads complete')
            if kona.progress_files_present():
                avalon.info('Removing progress file')
                kona.remove_progress_files()
    else:
        avalon.error('This file cannot be imported as a module!')
        raise SystemError('Cannot be imported')
except KeyboardInterrupt:
    avalon.warning('Ctrl+C detected in CLI Module')
    avalon.warning('Exiting program\n')
    exit(0)
except Exception:
    avalon.error('An error occurred during the execution of the program')
    traceback.print_exc()
    avalon.warning('This is critical information for fixing bugs and errors')
    avalon.warning('If you\'re kind enough wanting to help improving this program,')
    avalon.warning('please contact the developer.')
    exit(1)
