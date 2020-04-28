#!/usr/bin/env python3

import os
import glob
import csv
from zipfile import ZipFile
import contextlib
import logging
import datetime

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape


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


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

data = Data()

prefix = '.build/static'

def render(target, template, **kwargs):
    with open(f'{prefix}{target}', 'w') as stream:
        stream.write(env.get_template(f'{template}.html').render(**kwargs))


for person in data.people:
    url = f'/u/{person.name}/'
    os.makedirs(f'{prefix}{url}', exist_ok=True)
    posts = person.posts

    posts['ShareCommentary'] = (posts['ShareCommentary'].str.split(2*r'"\r\n"')
            .apply(lambda d: d if isinstance(d, list) else []))

    # TODO: posts = person.posts[posts['Visibility'] == 'MEMBER_NETWORK')
    #for post in posts.itertuples():
    #    print(post.ShareCommentary)
    render(f'{url}index.html', 'person-detail', url=url)
    render(f'{url}posts.html', 'post-list', posts=posts.itertuples())
render(f'/index.html', 'index', people=data.people)
