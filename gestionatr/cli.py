# -*- coding: utf-8 -*-
import sys
import click
from suds.cache import NoCache
from suds.client import Client
from suds.transport.https import HttpAuthenticated
import urllib2
import base64
from suds.sax.text import Raw
from lxml import objectify, etree

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
    with open(filename, 'r') as xml_file:
        try:
            data = xml_file.read()
            if sector == u'e':
                m = message.Message(data)
            elif sector == u'g':
                m = message_gas.MessageGas(data)
            m.parse_xml()
            sys.stdout.write(u'Correct File\n')
        except except_f1 as e:
            error_txt = unicode(e.value).encode(errors='ignore')
            sys.stdout.write(
                u'WARNING: Invalid File: {0}\n'.format(error_txt)
            )
        except Exception as e:
            error_txt = unicode(e).encode(errors='ignore')
            sys.stdout.write(
                u'WARNING: Invalid File: {0}\n'.format(error_txt)
            )
        finally:
            sys.stdout.flush()


def request_p0(url, user, password, xml_file):
    t = HttpAuthenticated(username=user, password=password)
    base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
    authenticationHeader = {
        "Authorization": "Basic %s" % base64string
    }
    try:
        client = Client(url, transport=t, retxml=True)
    except urllib2.URLError as e:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        client = Client(url, transport=t, retxml=True)
    client.set_options(headers=authenticationHeader)
    if isinstance(xml_file, str):
        xml_str = xml_file
    else:
        xml_str = xml_file

    # Clean XML
    xml_str = xml_str.strip()
    xml_str = xml_str.replace("'utf-8'", "'UTF-8'")
    xml_str = xml_str.replace("<?xml version='1.0' encoding='UTF-8'?>", "")
    xml_str = Raw(xml_str)
    # Send request
    res = client.service.sync(xml_str)
    try:
        aux = etree.fromstring(res)
        res = etree.tostring(aux[0][0][0][0])
    except Exception:
        pass
    return res


@atr.command(name='p0')
@click.option('-u', '--url', default='http://localhost', help=u'URL del webservice', show_default=True)
@click.option('-s', '--user', default='admin', help=u'User del webservice', show_default=True)
@click.option('-p', '--password', default='admin', help=u'Password del webservice', show_default=True)
@click.option('-f', '--file', help=u'Fitxer P0 pas 01 per enviar', show_default=True)
def sollicitar_p0(url, user, password, file):
    res = request_p0(url, user, password, file)
    print(res)


