# -*- coding: utf8 -*-
"""
    botly.py - A bitly Willie module

    It shortens the URLs from the chanel using bit.ly API
    and offers some features from the bitly's API.

    Commands: .last, .expand, .clicks
"""


import re
import bitly_api
from willie.module import rule
from willie.module import example
from willie.module import commands
from willie.config import ConfigurationError


# Not a hack. It's a walk around.
RE_URL = r'https?://\S*'
RE_HAS_URL = r'.*(' + RE_URL + ').*'


def configure(config):
    """
        | [botly] | example | purpose |
        | ---- | ------- | ------- |
        | access_token | default123 | The access token for Bitly |
    """

    # Access token for usign Bitly's API
    # cf. https://github.com/bitly/bitly-api-python/blob/master/README.md
    if config.option('Configure Botly', True):
        config.add_section('botly')
        config.interactive_add(
            'botly',
            'access_token',
            'Enter the access token for Bitly:',
            'default123'
        )
        config.interactive_add(
            'botly',
            'max_length',
            'Enter the max length that an URL can be:',
            79
        )


def setup(bot):
    if not bot.config.has_option('botly', 'access_token'):
        raise ConfigurationError(
            'Botly needs the access token in order to use the Bitly API'
        )
    if not bot.config.has_option('botly', 'max_length'):
        bot.config.botly['max_length'] = 79
    else:
        try:
            bot.config.botly.max_length = int(bot.config.botly.max_length)
        except ValueError:  # Back to the default value
            bot.config.botly['max_length'] = 79

    regex = re.compile(RE_HAS_URL)
    if not bot.memory.contains(u'url_callbacks'):
        bot.memory[u'url_callbacks'] = {regex, bitly_url}
    else:
        exclude = bot.memory[u'url_callbacks']
        exclude[regex] = bitly_url
        bot.memory[u'url_callbacks'] = exclude

    if not bot.memory.contains(u'bitly_client'):
        bot.memory[u'bitly_client'] = bitly_api.Connection(
            access_token=bot.config.botly.access_token
        )


@rule(RE_HAS_URL)
def bitly_url(bot, trigger):
    urls = re.findall(RE_URL, trigger)

    if bot.memory.contains(u'bitly_client'):
        for url in urls:
            if len(url) > bot.config.botly.max_length:
                try:
                    bot.memory[u'bitly_url'] = bot.memory[
                        u'bitly_client'
                    ].shorten(url)
                    bot.say(bot.memory[u'bitly_url'][u'url'])
                except bitly_api.BitlyError as e:
                    # If Bitly failed, we do nothing.
                    # Can happen when the matched url is already a bit.ly.
                    pass


@commands('last', 'lastest', 'new', 'newest')
@example('.last')
def bitly_last_url(bot, trigger):
    """Display the shortened version of the last URL using bitly."""

    if bot.memory.contains(u'bitly_url'):
        bot.say(trigger.nick + ': ' + bot.memory[u'bitly_url'][u'url'])


@commands('expand', 'long')
@example('.expand')
def bitly_expand_url(bot, trigger):
    """Display the expanded version of the last bitly URL."""

    if bot.memory.contains(u'bitly_url'):
        bot.say(trigger.nick + ': ' + bot.memory[u'bitly_url'][u'long_url'])


@commands('clicks')
@example('.clicks')
def bitly_clicks(bot, trigger):
    """Display the statistics about the user clicks on the last bitly URL."""

    if bot.memory.contains(u'bitly_client') and \
            bot.memory.contains(u'bitly_url'):
        bot.say(
            trigger.nick +
            ': ' +
            str(
                bot.memory[u'bitly_client'].link_clicks(
                    bot.memory[u'bitly_url'][u'url']
                )
            ) +
            ' click(s) on ' +
            bot.memory[u'bitly_url'][u'url']
        )
