#!/usr/bin/python3
try:
    import feedparser
    import discord
    import asyncio
    from os import stat, listdir
except ModuleNotFoundError:
    print("Missing a module. Please check discord.py is installed.")
    from time import sleep
    sleep(2)
    exit(1)

def get_embed(data):
    embeds = []
    for each in data:
        title = each["title"]
        summary = each["summary"]
        author = each["author"]
        link = each["comments"]
        time = each["published"].replace("+0000", "UTC")

        embed = discord.Embed(title="New Torrent", colour=0x21ff00)
        embed.add_field(name="Title", value=title, inline=False)
        embed.add_field(name="Summary", value=summary, inline=False)
        embed.add_field(name="Link", value=link, inline=False)
        embed.add_field(name="Author", value=author, inline=False)
        embed.add_field(name="Published", value=time, inline=False)
        embed.set_footer(text="Made by Seraph2")
        embeds.append(embed)
    return embeds

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create background task loop
        self.bg_task = self.loop.create_task(self.announce_torrents())        

    async def on_ready(self):
        print("Logged in as " + self.user.name)

    async def announce_torrents(self):
        await self.wait_until_ready()
        announce_channel = self.get_channel(713468778322853999) # this is the channel I used for testing, replace this with the channel you would like to use for announces
        while not self.is_closed():
            self.feed = feedparser.parse("https://aither.cc/rss/48.e99367ccad6938825c2e315feab20fc8")
            log = []
            if "log.txt" in listdir():
                with open("log.txt", "r") as f:
                    for each in f.read().split("\n\n"):
                        log.append(each)
            else:
                new = [x for x in self.feed["entries"]]
                embeds = get_embed(new)
                for each in embeds:
                    await announce_channel.send(embed=each)
                with open("log.txt", "w") as f:
                    for each in self.feed["entries"]:
                        f.write(str(each))
                        f.write("\n\n")
            new = [x for x in self.feed["entries"] if str(x) not in log]
            if len(new) > 0:
                embeds = get_embed(new)
                for each in embeds:
                    await announce_channel.send(embed=each)
                with open("log.txt", "w") as f:
                    for each in self.feed["entries"]:
                        f.write(str(each))
                        f.write("\n\n")

            await asyncio.sleep(15)
        
client = MyClient()
client.run("token goes here")
