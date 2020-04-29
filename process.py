#!/usr/bin/env python3

import os
import logging
import re

from jinja2 import Environment, FileSystemLoader, select_autoescape


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

from linkedin.archives import data

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

prefix = '.build/static'

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


for person in data.people:
    url = f'/out/{person.name}/'
    os.makedirs(f'{prefix}{url}/posts', exist_ok=True)
    posts = person.posts

    posts['ShareCommentary'] = posts['ShareCommentary'].apply(text_to_html)

    # TODO: posts = person.posts[posts['Visibility'] == 'MEMBER_NETWORK')
    #for post in posts.itertuples():
    #    print(post.ShareCommentary)
    render(f'{url}index.html', 'person-detail', url=url)
    render(f'{url}posts/index.html', 'post-list', posts=posts.itertuples())
render(f'/index.html', 'index', people=data.people)
