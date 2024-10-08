import os
import discord
import praw
import asyncio
from discord.ext import commands

# Set up the Reddit client
reddit = praw.Reddit(
    client_id='7DiD0cU_gsUE7-hCAC2fFA',
    client_secret='K-MdR75pqpLvfo_LYB1UXlE7Vq4xYg',
    user_agent='unixporn/1.0 by niyakipham'
)

# Set up the Discord bot
intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Function to scrape the latest post from r/unixporn
async def get_latest_unixporn_post():
    subreddit = reddit.subreddit('unixporn')
    latest_post = next(subreddit.new(limit=1))  # Get the newest post
    return {
        'title': latest_post.title,
        'image': latest_post.url if latest_post.url.endswith(('.jpg', '.png')) else None,
        'permalink': f"https://reddit.com{latest_post.permalink}"
    }

# Send the latest post to a specific Discord channel
@bot.command(name='fetch_unixporn')
async def fetch_unixporn(ctx):
    post = await get_latest_unixporn_post()
    if post['image']:
        embed = discord.Embed(title=post['title'], url=post['permalink'])
        embed.set_image(url=post['image'])
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"Latest post: {post['title']} \n{post['permalink']}")

# Bot ready event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(1291045191687475230)
    
    # Periodically fetch and post the latest Unixporn post every 10 minutes
    while True:
        post = await get_latest_unixporn_post()
        if post['image']:
            embed = discord.Embed(title=post['title'], url=post['permalink'])
            embed.set_image(url=post['image'])
            await channel.send(embed=embed)
        else:
            await channel.send(f"Latest post: {post['title']} \n{post['permalink']}")
        await asyncio.sleep(600)  # Wait for 10 minutes

# Run the bot with the token
bot.run(os.getenv('UNIX_TOKEN'))