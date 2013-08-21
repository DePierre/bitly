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


# Dumb regex for matching url link. Must be improved imo.
RE_URL = '.*(?P<url>(http|https)://\S*)'
# Access token for usign Bitly's API
# cf. https://github.com/bitly/bitly-api-python/blob/master/README.md
ACCESS_TOKEN = 'access_token'


def setup(bot):

    regex = re.compile(RE_URL)
    if not bot.memory.contains('url_callbacks'):
        bot.memory['url_callbacks'] = {regex, bitly_url}
    else:
        exclude = bot.memory['url_callbacks']
        exclude[regex] = bitly_url
        bot.memory['url_callbacks'] = exclude

    if not bot.memory.contains('bitly_api'):
        bot.memory['bitly_client'] = bitly_api.Connection(access_token=ACCESS_TOKEN)


@rule(RE_URL)
def bitly_url(bot, trigger):
    if bot.memory.contains('bitly_client'):
        try:
            url = bot.memory['bitly_client'].shorten(trigger.group('url'))
            bot.memory['bitly_url'] = url
            bot.say(url['url'])
        except bitly_api.BitlyError:
            # If Bitly failed, we do nothing.
            # Can happen when the matched url is already a bit.ly.
            pass


@commands('last', 'lastest', 'new', 'newest')
@example('.last')
def bitly_last_url(bot, trigger):
    """Display the shortened version of the last URL using bitly."""

    if bot.memory.contains('bitly_url'):
        bot.say(trigger.nick + ': ' + bot.memory['bitly_url']['url'])


@commands('expand', 'long')
@example('.expand')
def bitly_expand_url(bot, trigger):
    """Display the expanded version of the last bitly URL."""

    if bot.memory.contains('bitly_url'):
        bot.say(trigger.nick + ': ' + bot.memory['bitly_url']['long_url'])


@commands('clicks')
@example('.clicks')
def bitly_clicks(bot, trigger):
    """Display the statistics about the user clicks on the last bitly URL."""

    if bot.memory.contains('bitly_client') and bot.memory.contains('bitly_url'):
        bot.say(
            trigger.nick + ': ' +
            str(bot.memory['bitly_client'].user_clicks()[u'total_clicks']) +
            ' click(s) on ' +
            bot.memory['bitly_url']['url']
        )
