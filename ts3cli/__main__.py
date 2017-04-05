from operator import itemgetter

import click
from ts3py import TS3Query


@click.group()
@click.option('--host', help='teamspeak query host', required=True)
@click.option(
    '--port', type=int, help='teamspeak query port', default=10011,
    required=True
)
@click.option('--username', help='query username', required=True)
@click.option('--password', help='query password', required=True)
@click.pass_context
def ts3cli(ctx, host, port, username, password):
    query = TS3Query(host, port)
    query.login(username, password)
    ctx.obj = {}
    ctx.obj['query'] = query


@ts3cli.command()
@click.pass_context
def server(ctx):
    click.echo(list(map(
        itemgetter('virtualserver_name'),
        ctx.obj['query'].command('serverlist')
    )))


if __name__ == '__main__':
    ts3cli()
