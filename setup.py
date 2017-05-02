from setuptools import setup

setup(
    name='ts3cli',
    version='0.1.0',
    author='Thor77',
    author_email='thor77@thor77.org',
    description='CLI for Teamspeak 3\'s query interface',
    keywords='ts3 teamspeak teamspeak3 ts3cli cli',
    url='https://github.com/Thor77/TS3CLI',
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
