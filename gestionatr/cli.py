# -*- encoding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import six
import sys
import click

from gestionatr.input.messages import message
from gestionatr.input.messages import message_gas
from gestionatr.input.messages.message import except_f1

from gestionatr import __version__


VERSION_TEXT = u'ATR library version (gestionatr) : {0}'.format(__version__)


def get_gestionatr_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(VERSION_TEXT)
    ctx.exit()


@click.group()
@click.option("--version", "-v", is_flag=True, callback=get_gestionatr_version,
              expose_value=False, is_eager=True, help="ATR library version")
def atr():
    pass

@atr.command(name='test')
@click.option("--filename", "-f", help="path to XML filename", required=True)
@click.option("--sector", "-s", help="e (power) or g (gas)", default="e")
def test(filename, sector):
    with open(filename, 'rb') as xml_file:
        try:
            data = xml_file.read()
            if sector == 'e':
                m = message.Message(data)
            elif sector == 'g':
                m = message_gas.MessageGas(data)
            m.parse_xml()
            sys.stdout.write('Correct File\n')
        except except_f1 as e:
            error_txt = six.text_type(e.value).encode(errors='ignore')
            sys.stdout.write(
                'WARNING: Invalid File: {0}\n'.format(error_txt)
            )
        except Exception as e:
            error_txt = six.text_type(e).encode(errors='ignore')
            sys.stdout.write(
                'WARNING: Invalid File: {0}\n'.format(error_txt)
            )
        finally:
            sys.stdout.flush()
