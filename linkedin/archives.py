import glob
import csv
from zipfile import ZipFile
import datetime
import contextlib

import logging
log = logging.getLogger("linkedin.archives")

import pandas as pd

class Data:
    def __init__(self):
        self.people = [Person(p) for p in glob.glob('data/*')]


class Person:
    def __init__(self, path):
        self.name = path.split('/')[-1]
        self.archives = []
        for p in sorted(glob.glob(f'{path}/*.zip'), key=self._extract_archive_date):
            self.archives.append(Archive(p))
            with contextlib.suppress(AttributeError):
                print(len(self.archives[-1].posts))

    @staticmethod
    def _extract_archive_date(path):
        return datetime.datetime.strptime(path.split('_')[-1], '%m-%d-%Y.zip')

    @property
    def posts(self):
        for a in self.archives:
            with contextlib.suppress(AttributeError):
                posts = a.posts
        return posts


class Archive:
    def __init__(self, path):
        with ZipFile(path) as zipfile:
            log.debug(f"Processing: {path}")
            with contextlib.suppress(KeyError):
                with zipfile.open('Shares.csv') as stream:
                    self.posts = pd.read_csv(stream, parse_dates=['Date'])
                    self.posts.set_index(self.posts['Date'].dt.strftime('%Y%m%d-%H%M%S'), inplace=True)
                    self.posts['ShareCommentary'] = self.posts['ShareCommentary'].str.replace('"\r\n"', '\n')


data = Data()
