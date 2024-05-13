import discord
from   discord import app_commands
from   database import SimpleSQLiteDatabase
import logging
import common

#INIT VARS--------------------------------------
client = discord.Client(intents=discord.Intents.all())
tree   = app_commands.CommandTree(client)
#----------------------------------------------

def run_discord_bot():
    my_database = SimpleSQLiteDatabase('my_database.db')
    common.DB   = my_database
    logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    @client.event
    async def on_ready():
        await tree.sync(guild=discord.Object(id=common.SERVER_ID))
        print(f'{client.user} is now running!')
        logging.info(f'{client.user} is now running!')
    client.run(common.BOT_TOKEN)