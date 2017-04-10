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
        lambda vs: '{virtualserver_name} ({virtualserver_id}) - '
        '{virtualserver_clientsonline} clients online'.format(**vs),
        ctx.obj['query'].command('serverlist')
    )))


@ts3cli.command()
@click.option('--message', help='global message', required=True)
@click.pass_context
def gm(ctx, message):
    ctx.obj['query'].command('gm', params={'msg': message})


@ts3cli.command()
@click.option('--sid', help='virtual server id', default=1)
@click.pass_context
def clients(ctx, sid):
    ctx.obj['query'].command('use', params={'sid': sid})
    click.echo(list(map(
        itemgetter('client_nickname'),
        filter(
            lambda c: c['client_type'] == 0,
            ctx.obj['query'].command('clientlist')
        )
    )))


if __name__ == '__main__':
    ts3cli()
