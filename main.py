from typing import Final
import os
from dotenv import load_dotenv
import discord
import requests
import random
from discord.ext import commands

url = "REDACTED"
querystring = {
    "meta_property": "scientific_classification",
    "property_value": "actinopterygii",
    "meta_property_attribute": "class"
}

headers = {
    "x-rapidapi-key": "REDACTED",
    "x-rapidapi-host": "fish-species.p.rapidapi.com"
}

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

user_bal = {}

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

@bot.tree.command(name="fish", description="Cast a rod and catch a fish")
async def castA_Rod(interaction: discord.Interaction):
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        
        randID = random.randint(1, 1100)
        randCost = random.randint(1, 9999)
        species = ""
        photoURL = ""

        for fish in data:
            if fish.get("id") == randID: 
                species = fish.get("name")
                photoURL = fish.get("img_src_set", {}).get("2x")
                break

        user_id = interaction.user.id
        if user_id not in user_bal:
            user_bal[user_id] = 0 

        if species and photoURL:
            user_bal[user_id] += randCost
            embed = discord.Embed(title=f'You caught a {species}!', color=0x088F8F)
            embed.set_image(url=photoURL)
            embed.add_field(name='Value', value=f'${randCost}', inline=True)
            embed.add_field(name='New Balance', value=f'${user_bal[user_id]}', inline=True)

            # Determine rarity and add it as a field in the embed
            if randCost >= 9990:
                embed.add_field(name='Rarity', value='This catch is Ultra Rare!', inline=False)
            elif randCost >= 5000:
                embed.add_field(name='Rarity', value='This catch is Rare!', inline=False)
            elif randCost >= 1000:
                embed.add_field(name='Rarity', value='This catch is Common!', inline=False)
            elif randCost >= 500:
                embed.add_field(name='Rarity', value='This catch is... Well, it\'s something!', inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("You caught nothing.")
    else:
        await interaction.response.send_message(f"Error fetching fish data: {response.status_code}")

@bot.tree.command(name="gamble", description="Time to Risk it All")
async def gambaTime(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in user_bal:
        user_bal[user_id] = 0

    if user_bal[user_id] != 0:
        fiftyfifty = random.randint(1, 100)
        if (fiftyfifty >= 99):
            user_bal[user_id] *= 14
            await interaction.response.send_message(f'You rolled on the GREEN! Your new balance is ${user_bal[user_id]}')
        elif (fiftyfifty > 50):
            user_bal[user_id] *= 2
            await interaction.response.send_message(f'You won! Your new balance is ${user_bal[user_id]}')
        else:
            user_bal[user_id] = 0
            await interaction.response.send_message(f'You lost! Your new balance is ${user_bal[user_id]}')
    else:
        await interaction.response.send_message(f'You have no money to gamble! \n Try Fishing to make some money!')

@bot.tree.command(name="balance", description="Checkin that Cheddar")
async def cheddarChecker(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in user_bal:
        user_bal[user_id] = 0

    await interaction.response.send_message(f'You currently have ${user_bal[user_id]}')

# Start the bot
bot.run(TOKEN)
