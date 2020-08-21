#!/usr/bin/python3
try:
    import feedparser
    import discord
    import asyncio
    from hashlib import md5
    from os import stat, listdir
    
except ModuleNotFoundError:
    print("Missing a module. Please check discord.py is installed.")
    from time import sleep
    sleep(2)
    exit(1)

def parseSize(text):
    regex = r"Size<\/strong>: \d+\.?\d*"
    matches = re.finditer(regex, text, re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        size = match.group()
    size = size.split(": ")[1] + " GiB"
    return size

def get_embed(data):
    embeds = []
    for each in data:
        title = each["title"]
        summary = each["category"]
        size = parseSize(each["summary"])
        link = each["link"]
        author = each["authors"][0]["name"]
        time = each["published"].replace("+0000", "UTC")

        embed = discord.Embed(title="New Torrent", colour=0x21ff00)
        embed.add_field(name="Title", value=title, inline=False)
        embed.add_field(name="Category", value=summary, inline=False)
        embed.add_field(name="Size", value=size, inline=False)
        embed.add_field(name="Link", value=link, inline=False)
        embed.add_field(name="Author", value=author, inline=False)
        embed.add_field(name="Published", value=time, inline=False)
        embed.set_footer(text="Made by Seraph2")
        embeds.append(embed)
    return embeds

def get_embed_modified(data):
    embeds = []
    for each in data:
        title = each["title"]
        summary = each["category"]
        link = each["link"]
        author = each["authors"][0]["name"]
        time = each["published"].replace("+0000", "UTC")

        embed = discord.Embed(title="Torrent Updated", colour=0x9400D3)
        embed.add_field(name="Title", value=title, inline=False)
        embed.add_field(name="Category", value=summary, inline=False)
        embed.add_field(name="Link", value=link, inline=False)
        embed.add_field(name="Author", value=author, inline=False)
        embed.add_field(name="Published", value=time, inline=False)
        embed.set_footer(text="Made by Seraph2")
        embeds.append(embed)
    return embeds

# returns an md5 hash made from the uploader and publish time of a torrent. this is used to check whether it really is a new torrent or an edit of a previous one.
def get_identifier(entry):
    author = entry["authors"][0]["name"]
    time = entry["published"].replace("+0000", "UTC")
    combined = str(time) + str(author)
    identifier = md5(combined.encode())
    return identifier.hexdigest()

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create background task loop
        self.bg_task = self.loop.create_task(self.announce_torrents())        

    async def on_ready(self):
        print("Logged in as " + self.user.name)

    async def announce_torrents(self):
        await self.wait_until_ready()
        announce_channel = self.get_channel(715229124230250527) # this is the channel I used for testing, replace this with the channel ID you would like to use for announces
        while not self.is_closed():
            self.feed = feedparser.parse("https://aither.cc/rss/56.e99367ccad6938825c2e315feab20fc8")
            log = []
            current_hashes = list(map(get_identifier, self.feed["entries"]))
            hashes = []
            # check if torrent log exists
            if "log.txt" in listdir():
                with open("log.txt", "r") as f:
                    for each in f.read().split("\n\nSEPERATOR\n\n"):
                        log.append(each)
                #check if torrent hashes exist
                if "hashes.txt" in listdir():
                    with open("hashes.txt", "r") as f:
                        for each in f.read().split("\n\n"):
                            hashes.append(each)
                    
                    new = [x for x in self.feed["entries"] if str(x) not in log and str(get_identifier(x)) not in hashes]
                    #modified = [x for x in self.feed["entries"] if str(x) not in log and str(get_identifier(x)) in hashes]
            # announce and write to files if no log exists
            else:
                new = [x for x in self.feed["entries"]]
                embeds = get_embed(new)
                for each in embeds:
                    await announce_channel.send(embed=each)
                with open("log.txt", "w") as f:
                    for each in self.feed["entries"]:
                        f.write(str(each))
                        f.write("\n\nSEPERATOR\n\n")
                with open("hashes.txt", "w") as f:
                    for each in hashes:
                        f.write(str(each))
                        f.write("\n\n")

            if len(new) > 0: #or len(modified) > 0:
                try:
                    newEmbeds = get_embed(new)
                except Exception as e:
                    print(str(e))
                #try:
                    #modifiedEmbeds = get_embed_modified(modified)
                #except Exception as e:
                    #print(str(e))
                try:
                    embeds = newEmbeds# + modifiedEmbeds
                    for each in embeds:
                        await announce_channel.send(embed=each)
                    with open("log.txt", "w") as f:
                        for each in self.feed["entries"]:
                            f.write(str(each))
                            f.write("\n\nSEPERATOR\n\n")
                    with open("hashes.txt", "w") as f:
                        for each in current_hashes:
                            f.write(str(each))
                            f.write("\n\n")
                except Exception as e:
                    print(str(e))
            await asyncio.sleep(15)
        
client = MyClient()
client.run("token goes here")
