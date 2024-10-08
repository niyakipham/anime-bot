import discord
import requests
from bs4 import BeautifulSoup
import os
import asyncio

# Discord client setup
intents = discord.Intents.default()
intents.messages = True
bot = discord.Client(intents=intents)

# Channel ID where the bot will send updates
CHANNEL_ID = 1292039065440485450 # Replace with your actual Discord channel ID

# Kodoani URL
URL = "https://kodoani.com/"

# Function to fetch the latest post from Kodoani
def get_latest_kodoani_post():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the latest post (adjust selectors according to website structure)
    latest_post = soup.find('div', class_='block-posts')  # Adjust this selector according to website structure
    if not latest_post:
        return None

    # Extract the necessary information from the post
    post_title = latest_post.find('h2').text.strip()
    post_url = latest_post.find('a')['href']
    post_image = latest_post.find('img')['src']

    post_info = {
        "title": post_title,
        "url": post_url,
        "image": post_image
    }
    return post_info

# Check for new post every X minutes
async def check_for_new_post():
    last_post_url = None

    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)
    
    while True:
        latest_post = get_latest_kodoani_post()
        
        if latest_post and latest_post['url'] != last_post_url:
            # New post detected, send it to the channel
            last_post_url = latest_post['url']
            embed = discord.Embed(title=latest_post['title'], url=latest_post['url'], description="New post on Kodoani!")
            embed.set_image(url=latest_post['image'])

            await channel.send(embed=embed)
        
        # Wait for 10 minutes before checking again
        await asyncio.sleep(20)

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Bot is ready and logged in as {bot.user}')
    bot.loop.create_task(check_for_new_post())

# Run tke sure your DISCORD_TOKEN is set in environment variables


# Run the bot with the token
bot.run(os.getenv('UNIXPORN_TOKEN'))