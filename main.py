import logging
import os
from configparser import SafeConfigParser
from random import randint

import discord
from discord.ext import commands
from nudenet import NudeClassifier
from nudenet import NudeDetector

logging.basicConfig(level=logging.INFO)

# config stuff
config = SafeConfigParser()
config.read('config.ini')

# bot config
bot_mode = config['bot']['mode']
debug = config.getboolean('bot', 'debug')
token = config['bot']['token']
clientid = config['bot']['clientid']
prefix = str(config['bot']['prefix'])
botperms = config['bot']['botperms']

# policy
denythreshold = config.getfloat('policy', 'denythreshold')
accepted_formats = config['policy']['acceptedfiles'].split(',')
allowtie = config.getboolean('policy', 'allow_ties')

bot = commands.Bot(command_prefix=prefix)
# nude detector is not used unless in debug, so you can see why some images are deemed nsfw
detector = NudeDetector()
classifier = NudeClassifier()


# cog loading
@bot.event
async def on_ready():
    invlink = f"https://discord.com/oauth2/authorize?client_id={clientid}&permissions={botperms}&scope=bot"
    print(f"lewd stopper is ready, invite me at link {invlink}")
    if debug:
        print(
            "==== WARNING: DEBUG MODE IS ON! NO MESSAGES WILL BE DELETED.====\n==== FOR THIS BOT TO MODERATE PROPERLY, "
            "TURN OFF DEBUG IN CONFIG.INI ====")

# this function will be ran async by the executor
def get_classification(image_loc):
    # print what the bot is detecting if we are in debug
    if debug:
        print(detector.detect(image_loc))
    verdict = classifier.classify(image_loc)[image_loc]
    # delete image after we are done
    os.remove(image_loc)
    # do math to check if unsafe and safe thresholds are about the same. if they are, assume image is unsafe
    # if safe is greater than unsafe and the difference is greater than the threshold, allow image
    if debug:
        print(verdict)
    if verdict['safe'] > verdict['unsafe'] and verdict['safe'] - verdict['unsafe'] > denythreshold:
        return 'safe'
    # same here, but in reverse
    elif verdict['unsafe'] > verdict['safe'] and verdict['unsafe'] - verdict['safe'] > denythreshold:
        return 'unsafe'
    else:
        # if its a toss-up, return tie
        return 'tie'


@bot.event
async def on_message(message):
    # are there actually attachements, and is the channel not nsfw?
    if len(message.attachments) > 0 and not message.channel.is_nsfw():
        for a in message.attachments:
            # is the file of acceptable format?
            for f in accepted_formats:
                if a.filename.lower().endswith(f):
                    # create a path
                    saveloc = f'temp/{randint(1, 1000)}{a.filename}'
                    # save the file to the save location
                    await a.save(saveloc)
                    verdict = await bot.loop.run_in_executor(None, get_classification, saveloc)
                    if debug:
                        print(f'Image from {str(message.author)}, verdict {verdict}')
                    else:
                        if verdict == "unsafe":
                            print(f'An unsafe message from {str(message.author)} was deleted.')
                            await message.delete()
                            embed = discord.Embed(
                                title='Unsafe content removed',
                                color=discord.Colour.red(),
                                description=f"I have automatically deemed a message sent by @{str(message.author)} "
                                            f"to be unsafe and have removed it."
                            )
                            embed.set_footer(text=f"Please contact an admin if you have any questions or concerns.")
                            await message.channel.send(embed=embed)
                        if verdict == "tie":
                            if not allowtie:
                                await message.delete()
                                print(f'A questionable message from {str(message.author)} was deleted.')
                                embed = discord.Embed(
                                    title='Questionable content removed',
                                    color=discord.Colour.orange(),
                                    description=f"I have automatically deemed a message sent by @{str(message.author)} "
                                                f"to be questionable and have removed it due to my current settings."
                                )
                                embed.set_footer(text=f"Please contact an admin if you have any questions or concerns.")
                                await message.channel.send(embed=embed)
    await bot.process_commands(message)


bot.run(token)
