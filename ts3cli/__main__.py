# -*- coding: utf-8 -*-
from datetime import timedelta

import click
from ts3py import TS3Query

from .utils import (cid_option, clid_option, count_to_str, msg_option,
                    pass_query, sid_option, use)


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
    ctx.obj = query


@ts3cli.resultcallback()
@pass_query
def disconnect(query, *args, **kwargs):
    # disconnect from query
    query.command('quit')


@ts3cli.command()
@pass_query
def server(query):
    '''
    List virtual servers
    '''
    click.echo(', '.join(map(
        lambda vs: '{virtualserver_name} ({virtualserver_id}) - '
        '{clientsonline}'.format(
            clientsonline=count_to_str(
                vs['virtualserver_clientsonline'], 'client'
            ) + ' online',
            **vs
        ),
        query.command('serverlist')
    )))


@ts3cli.command()
@msg_option
@pass_query
def gm(query, msg):
    '''
    Send a global message
    '''
    query.command('gm', params={'msg': msg})


@ts3cli.command()
@sid_option
@pass_query
def clients(query, sid):
    '''
    List clients on a virtual server
    '''
    use(query, sid)
    click.echo(', '.join(map(
        lambda client: '{client_nickname} ({clid})'.format(**client),
        filter(
            lambda c: c['client_type'] == 0,
            query.command('clientlist')
        )
    )))


@ts3cli.command()
@sid_option
@clid_option
@pass_query
def clientinfo(query, sid, clid):
    '''
    View detailed information about a client
    '''
    use(query, sid)
    client_info = query.command(
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
Connection time: {connection_time}
Channel (ID): {cid}'''.format(
            clid=clid, connection_time=timedelta(
                milliseconds=client_info['connection_connected_time']),
            **client_info
        )
    )


@ts3cli.command()
@sid_option
@pass_query
def channel(query, sid):
    '''
    List channel on a virtual server
    '''
    use(query, sid)
    click.echo(', '.join(map(
        lambda channel: '{channel_name} ({cid}){clients}'.format(
            clients=' - {}'.format(
                count_to_str(channel['total_clients'], 'client')
            ) if channel['total_clients'] >= 1 else '',
            **channel
        ),
        query.command('channellist')
    )))


@ts3cli.command()
@sid_option
@cid_option
@pass_query
def channelinfo(query, sid, cid):
    '''
    View detailed information about a channel
    '''
    use(query, sid)
    channel_info = query.command(
        'channelinfo', params={'cid': cid})[0]
    click.echo(
        '''Name: {channel_name}
Topic: {channel_topic}
Description: {channel_description}
Password: {password}
Type: {type}
Max clients: {maxclients}
Filepath: {channel_filepath}
Icon: {channel_icon_id}
'''.format(
            password='yes' if channel_info['channel_password'] else 'no',
            maxclients=(
                '∞' if channel_info['channel_maxclients'] == -1
                else channel_info['channel_maxclients']
            ),
            type=list(filter(lambda t: t[1], [
                ('permanent', channel_info['channel_flag_permanent']),
                (
                    'semi_permanent',
                    channel_info['channel_flag_semi_permanent']
                ),
                ('temporary', 1)
            ]))[0][0],
            **channel_info
        )
    )


@ts3cli.command()
@sid_option
@clid_option
@msg_option
@pass_query
def poke(query, sid, clid, msg):
    '''
    Poke a client
    '''
    use(query, sid)
    query.command('clientpoke', params={'clid': clid, 'msg': msg})


@ts3cli.command()
@sid_option
@clid_option
@click.option('--reason', help='kick reason')
@click.option(
    '--channel', help='kick from channel', is_flag=True, default=False
)
@pass_query
def kick(query, sid, clid, reason, channel):
    '''
    Kick a client
    '''
    use(query, sid)
    params = {
        'clid': clid,
        'reasonid': 4 if channel else 5
    }
    if reason:
        params['reasonmsg'] = reason
    query.command('clientkick', params=params)


@ts3cli.command()
@sid_option
@clid_option
@click.option(
    '--duration',
    type=int, help='ban duration in seconds (if not given permanent)'
)
@click.option('--reason', help='ban reason')
@pass_query
def ban(query, sid, clid, duration, reason):
    '''
    Ban a client
    '''
    use(query, sid)
    params = {
        'clid': clid
    }
    if duration:
        params['time'] = duration
    if reason:
        params['banreason'] = reason
    query.command('banclient', params=params)


@ts3cli.command()
@sid_option
@pass_query
def banlist(query, sid):
    '''
    List bans
    '''
    use(query, sid)
    click.echo(', '.join(map(
        lambda ban: '{identifier} ({banid})'.format(
            identifier=ban['ip'] if ban['ip']
                    else '{nickname}{uid}'.format(
                        nickname=(
                            ban['lastnickname'] + '/'
                            if ban['lastnickname'] else ''
                        ),
                        **ban
                    ),
            **ban
        ),
        query.command('banlist')
    )))


@ts3cli.command()
@sid_option
@click.option('--banid', help='ban id', required=True)
@pass_query
def bandel(query, sid, banid):
    '''
    Remove a ban
    '''
    use(query, sid)
    query.command('bandel', params={'banid': banid})


if __name__ == '__main__':
    ts3cli()
