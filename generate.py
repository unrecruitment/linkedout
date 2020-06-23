#!/usr/bin/env python3

import os
import glob
import logging
import re
import datetime
import types

from jinja2 import Environment, FileSystemLoader, select_autoescape


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

import ruamel.yaml
yaml = ruamel.yaml.YAML()

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

prefix = 'build_dir/static'

def render(target, template, **kwargs):
    with open(f'{prefix}{target}', 'w') as stream:
        stream.write(env.get_template(f'{template}.html').render(**kwargs))

def text_to_html(text):
    if not isinstance(text, str):
        return ''
    result = []
    for p in text.split('\n\n'):
        p = re.sub(r'#([a-zA-Z0-9]+)', r'<b>#\1</b>', p)
        p = '<p>' + p.replace('\n', '<br>') + '</p>'
        result.append(p)
    return ''.join(result)
env.filters['text_to_html'] = text_to_html

def preprocess(posts):
    for key, value in posts.items():
        value['Date'] = datetime.datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
        yield types.SimpleNamespace(**value)

people = [types.SimpleNamespace(path=path, name=path.split('/')[-1])
        for path in glob.glob('data/users/*')]

for person in people:
    url = f'/out/{person.name}/'
    os.makedirs(f'{prefix}{url}/posts', exist_ok=True)
    with open(f'{person.path}/posts.yaml') as stream:
        posts = yaml.load(stream)['posts']

    # TODO: posts = person.posts[posts['Visibility'] == 'MEMBER_NETWORK')
    #for post in posts.itertuples():
    #    print(post.ShareCommentary)
    render(f'{url}index.html', 'person-detail', url=url)
    render(f'{url}posts/index.html', 'post-list', posts=preprocess(posts))
render(f'/index.html', 'index', people=people)
