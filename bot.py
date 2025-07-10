import discord
import feedparser
import asyncio
import html
import re
import os

# Token environment variable se lo (Render.com pe set karna hoga)
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1392691822031011920

RSS_URL = 'https://www.google.com/alerts/feeds/13510503719776267187/13280506720248693602'

intents = discord.Intents.default()
client = discord.Client(intents=intents)
posted_links = set()

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext)

async def fetch_and_post():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    while not client.is_closed():
        feed = feedparser.parse(RSS_URL)
        for entry in feed.entries:
            if entry.link not in posted_links:
                posted_links.add(entry.link)

                title = entry.title
                summary = ''
                if 'summary' in entry:
                    summary = clean_html(entry.summary)
                elif 'content' in entry and len(entry.content) > 0:
                    summary = clean_html(entry.content[0].value)

                img_url = None
                if 'summary' in entry:
                    img_match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
                    if img_match:
                        img_url = img_match.group(1)

                embed = discord.Embed(
                    title=title,
                    description=summary[:300] + ('...' if len(summary) > 300 else ''),
                    url=entry.link,
                    color=0x1a73e8
                )
                if img_url:
                    embed.set_thumbnail(url=img_url)
                embed.set_footer(text="Google Alerts Feed")

                await channel.send(embed=embed)
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    client.loop.create_task(fetch_and_post())

client.run(TOKEN)
