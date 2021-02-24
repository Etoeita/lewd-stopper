<img src="https://i.imgur.com/9oAXuo2.png" width="600">

# lewdStopper
lewdStopper is a Python 3.6 discord.py bot using <a href="https://github.com/notAI-tech/NudeNet">notAI-tech's "NudeNet" neural network</a>. It enforces keeping NSFW content
in NSFW channels on Discord, and will delete messages that it deems lewd, and if your settings are set to it, questionable material as well.


## Setup
Make a bot on https://discord.com/developers/applications. Then, paste your bot token into the config.ini.sample file on line 10, paste your client id in on 12, and rename config.ini.sample to config.ini. Simple.

The rest of the config.ini is optional, but it is the only part you should be touching unless you want to tinker with the code.  

## Usage
There are no commands, the bot automatically does everything. Any settings should be adjusted in config.ini.  

## How it works
Imagine a message is sent. The bot first checks if the message has a file attachment, and if the file is outside of an NSFW channel. If it is outside, the bot then checks if the file is of a supported format, and if it is, it is then ran, asynchronously, through nudeNET, which then returns a safe and unsafe score.  
The bot then checks which score is higher, and if the scores have a big enough difference (determined by the `denythreshold`) it will treat it accordingly, either deleting the image for being unsafe or not doing anything at all.  
If the scores are too close, a "tie" is determined and is then handled by your `allow_ties` settings, either keeping the image or removing it (this is what "questionable" means)

### What channels are "NSFW"?
Any channel with the NSFW toggle on. It is not determined by name, or manually.

## Requirements
Requirements are listed in requirements.txt and should be installed via `pip install -r requirements.txt`.

## Disclaimer
Don't forget, this is a *neural network*, and a computer making decisions. This may not be perfect! Do not use it to replace regular moderation. 
