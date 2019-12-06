import json
import tweepy
import discord
import asyncio
import requests
from discord.ext import commands
from datetime import timedelta
from config import bot_token, bot_owner_id, bad_words
from config import twitter_api_key, twitter_api_secret
from config import twitter_at, twitter_at_secret

bot = commands.Bot('!', self_bot=True)
url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_secret)
auth.set_access_token(twitter_at, twitter_at_secret)
api = tweepy.API(auth)


async def status_task():
    T = 0
    while True:
        switch = str(open("switch", "r").read())
        if switch == 'BTC':
            T = 0
            x = requests.get(url)
            data = json.loads(x.content)
            USD = data["bpi"]["USD"]["rate"].split('.', 1)[0] + " USD"
            await bot.change_presence(activity=discord.Streaming(
                name="{}".format("1 BTC = "+USD),
                url="http://twitch.tv/127.0.0.1",
                type=0))
            await asyncio.sleep(60)

        if switch == 'counter':
            text = ''
            with open("counter", "r") as co:
                text = co.read()
            await bot.change_presence(activity=discord.Streaming(
                name="{}".format(str(timedelta(seconds=int(T)))+' '+text),
                url="http://twitch.tv/127.0.0.1",
                type=0))
            await asyncio.sleep(20)
            T += 20


@bot.event
async def on_ready():
    print("noodles is online")
    bot.loop.create_task(status_task())


@bot.event
async def on_message(message):
    if str(message.author.id) == bot_owner_id:
        message_content = message.content.lower()

        if message_content.startswith('!count'):
            with open("switch", "w") as switch:
                switch.write('counter')
            with open("counter", "w") as co:
                co.write(message_content.replace('!count ', ''))
            await bot.delete_message(message)

        if message_content == '!btc':
            with open("switch", "w") as switch:
                switch.write('BTC')
            await bot.delete_message(message)

        if message_content.startswith('!tweet '):
            TW = str(message.content).replace('!tweet ', '')
            try:
                api.update_status(status=(TW))
            except Exception:
                pass

            try:
                latest_tweet = api.user_timeline(id=api.me().id, count=1)[0]
                new_tweet_name = str(latest_tweet.user.screen_name)
                new_tweet_id = str(latest_tweet.id_str)
                last_t = 'https://twitter.com/'+new_tweet_name+'/status/'+new_tweet_id
                embed = discord.Embed(
                    title=str(message.content.replace('!tweet ', '')),
                    description='[tweet link]('+last_t+')'+'   -    **`gucci toilet`**',
                    color=discord.Color(0x17181a))
                embed.set_author(
                    name='@'+str(latest_tweet.user.screen_name),
                    icon_url=str(latest_tweet.user.profile_image_url))
                await message.channel.send(embed=embed)

            except Exception:
                pass

        for words in message_content.split():
            if words in bad_words:
                await message.add_reaction("👀")


bot.run(bot_token, bot=False)
