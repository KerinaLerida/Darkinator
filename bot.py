import discord
from database import SimpleSQLiteDatabase
from discord import app_commands
import logging
import threading
import common
import time

#INIT VARS--------------------------------------
n=3600 # Update signal is produced each n seconds and champion is updated ONLY when ?guess command is called
choose_update=False
client = discord.Client(intents=discord.Intents.all())
tree=app_commands.CommandTree(client)
#-----------------------------------------------

def update_bool_guess(my_database):
    global choose_update
    while True:
        choose_update=True
        time.sleep(n)

def run_discord_bot():
    my_database = SimpleSQLiteDatabase('champions.db')
    common.DB=my_database
    logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @client.event
    async def on_ready():
        await tree.sync(guild=discord.Object(id=common.SERVER_ID))
        print(f'{client.user} is now running!')
        logging.info(f'{client.user} is now running!')

        logging.info("List of commands:")
        logging.info(len(tree.get_commands()))
        for command in tree.get_commands():
            logging.info(command.name)

    # Lancez la tâche périodique
    th = threading.Thread(target=update_bool_guess, args=(my_database,))
    th.start()

    # Remember to run your bot with your personal TOKEN
    client.run(common.BOT_TOKEN)


