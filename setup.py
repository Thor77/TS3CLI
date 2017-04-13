from setuptools import setup

setup(
    name='ts3cli',
    version='0.1.0',
    packages=['ts3cli'],
    install_requires=[
        'Click',
        'TS3Py'
    ],
    entry_points='''
        [console_scripts]
        ts3cli=ts3cli.__main__:ts3cli
    ''',
)
