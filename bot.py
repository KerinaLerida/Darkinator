import discord
from database import SimpleSQLiteDatabase
import logging
import responses
import asyncio
import threading
import time

#Update signal is produced each n seconds and champion is updated ONLY when ?guess command is called
n=3600
choose_update=False

def update_bool_guess(my_database):
    global choose_update
    while True:
        choose_update=True
        time.sleep(n)

"""async def update_bool_guess(my_database):
    hours,minutes =responses.how_long_guess_mode_active()
    while True:
        await asyncio.sleep(60)
        if hours<=0 and minutes<=0:
            responses.guess_mode(responses.hours_x,my_database)"""

def check_role(name_role, msg):
    verif_role = discord.utils.get(msg.guild.roles, name=name_role)
    if verif_role in msg.author.roles:
        return True
    return False

async def send_embed_message_with_file(message, embed, file):
    try:
        await message.channel.send(embed=embed, file=file)
    except Exception as e:
        print(e)
        logging.error(e)

# Send messages as embeds
async def send_embed_message(message, embed):
    try:
        await message.channel.send(embed=embed)
    except Exception as e:
        print(e)
        logging.error(e)

# Send messages
async def send_message(message, user_message, my_database):
    try:
        response = responses.handle_response(message, user_message, my_database)
        if isinstance(response, tuple) and len(response) == 2:
            embed, file = response
            await send_embed_message_with_file(message, embed, file)
        elif isinstance(response, discord.Embed):
            await send_embed_message(message, response)
        elif response:
            await message.channel.send(response)

    except Exception as e:
        print(e)
        logging.error(e)


def run_discord_bot():
    TOKEN = 'MTE0MDkyNTM5MDE3NzY5Nzc5Mg.G2FNf5.a3P8RME9KnMK_oD0k8lWsmQTwjIatOfja-S4z0'
    client = discord.Client(intents=discord.Intents.all())
    my_database = SimpleSQLiteDatabase('champions.db')
    logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        logging.info(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        # Make sure bot doesn't get stuck in an infinite loop
        if message.author == client.user:
            return

        # ******************** DEBUG ********************
        # Get data about the user
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        id_user = str(message.author.id)

        # ************************************************

        if message.channel.name == "🤖╿darkinia":
            if check_role("Cotisant", message):  # Vérifie : Role Cotisant nécessaire
                if user_message[0] == '?':
                    user_message = user_message[1:]  # [1:] Removes the '?'
                    await send_message(message, user_message, my_database)
                else:
                    return

    # Lancez la tâche périodique
    th = threading.Thread(target=update_bool_guess, args=(my_database,))
    th.start();

    # Remember to run your bot with your personal TOKEN
    client.run(TOKEN)

