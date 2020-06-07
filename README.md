# aither-announcer
## Requirements
- python 3
- discord.py
- A discord account
## Set-up
- Create a bot account on Discord and replace "token goes here" with your token. See [here](https://discordpy.readthedocs.io/en/latest/discord.html) for more information.
- Find the channel ID you would like to use for announces and replace the one in main.py (line 71)
- If no log.txt file is present the bot will announce every torrent in the RSS feed. This is because it has no log to compare to. After the log is created it will continue announcing only new torrents.
