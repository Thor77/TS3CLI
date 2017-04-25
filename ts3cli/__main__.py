from datetime import timedelta

import click
from ts3py import TS3Query

sid_option = click.option('--sid', help='virtual server id', default=1)
clid_option = click.option('--clid', help='client id', required=True)
msg_option = click.option('--msg', help='message', required=True)


@click.group()
@click.option('--host', help='teamspeak query host', default='localhost')
@click.option(
    '--port', type=int, help='teamspeak query port', default=10011,
)
@click.option('--username', help='query username', required=True)
@click.option('--password', help='query password', required=True)
@click.pass_context
def ts3cli(ctx, host, port, username, password):
    query = TS3Query(host, port)
    query.login(username, password)
    ctx.obj = {}
    ctx.obj['query'] = query


@ts3cli.resultcallback()
@click.pass_context
def disconnect(ctx, result, **kwargs):
    # disconnect from query
    ctx.obj['query'].command('quit')


@ts3cli.command()
@click.pass_context
def server(ctx):
    '''
    List virtual servers
    '''
    click.echo(', '.join(map(
        lambda vs: '{virtualserver_name} ({virtualserver_id}) - '
        '{virtualserver_clientsonline} clients online'.format(**vs),
        ctx.obj['query'].command('serverlist')
    )))


@ts3cli.command()
@msg_option
@click.pass_context
def gm(ctx, msg):
    '''
    Send a global message
    '''
    ctx.obj['query'].command('gm', params={'msg': msg})


@ts3cli.command()
@sid_option
@click.pass_context
def clients(ctx, sid):
    '''
    List clients on a virtual server
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    click.echo(', '.join(map(
        lambda client: '{client_nickname} ({clid})'.format(**client),
        filter(
            lambda c: c['client_type'] == 0,
            ctx.obj['query'].command('clientlist')
        )
    )))


@ts3cli.command()
@sid_option
@clid_option
@click.pass_context
def clientinfo(ctx, sid, clid):
    '''
    View detailed information about a client
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    client_info = ctx.obj['query'].command(
        'clientinfo', params={'clid': clid})[0]
    click.echo(
        '''Nickname: {client_nickname}
Description: {client_description}
ID: {clid}
Database ID: {client_database_id}
Unique Identifier: {client_unique_identifier}
Version/Platform: {client_version} on {client_platform}
IP: {connection_client_ip}
Country: {client_country}
Connection time: {connection_time}'''.format(
            **client_info, clid=clid, connection_time=timedelta(
                milliseconds=client_info['connection_connected_time'])
        )
    )


@ts3cli.command()
@sid_option
@clid_option
@msg_option
@click.pass_context
def poke(ctx, sid, clid, msg):
    '''
    Poke a client
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    ctx.obj['query'].command('clientpoke', params={'clid': clid, 'msg': msg})


@ts3cli.command()
@sid_option
@clid_option
@click.option('--reason', help='kick reason')
@click.option(
    '--channel', help='kick from channel', is_flag=True, default=False
)
@click.pass_context
def kick(ctx, sid, clid, reason, channel):
    '''
    Kick a client
    '''
    ctx.obj['query'].command('use', params={'sid': sid})
    params = {
        'clid': clid,
        'reasonid': 4 if channel else 5
    }
    if reason:
        params['reasonmsg'] = reason
    ctx.obj['query'].command('clientkick', params=params)


if __name__ == '__main__':
    ts3cli()
