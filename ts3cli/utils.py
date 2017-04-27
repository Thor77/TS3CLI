import click

sid_option = click.option('--sid', help='virtual server id', default=1)
cid_option = click.option('--cid', help='channel id', required=True)
clid_option = click.option('--clid', help='client id', required=True)
msg_option = click.option('--msg', help='message', required=True)
