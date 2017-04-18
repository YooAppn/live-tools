
from pip.req import parse_requirements
from setuptools import setup, find_packages

requires = [str(ir.req) for ir in parse_requirements('./requirements.txt', session='setup')]

setup(
    name='lt',
    description=(
        "live support tools for local network"
        "tools"
        " - chat"),
    version='0.0.1',
    packages=find_packages(),
    install_requires=requires,
    author='Woo Yoowaan',
    author_email='wooyoowaan@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 2.7.9',
    ],
    data_files=[
        ('livetools/statics', ['livetools/statics/chat.css', 'livetools/statics/chat.js']),
        ('livetools/templates', ['livetools/templates/index.html', 'livetools/templates/chatroom.html']),
        ],
    scripts=['livetools/bin/livetools'],
)
