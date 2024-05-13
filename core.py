import discord
import bot
import common
import datetime

n_coin = "ff"


def create_embed(title, description):
    color = discord.Color(0xb408ab)  # couleur msg embed
    return discord.Embed(title=title, description=description, color=color)


# get list of discord.Role and returns list of roles' names
def get_role_name(roleArray: list):
    return [i.name for i in roleArray]


# Command Validity checkers-------------------------
def check_roles(inter: discord.Interaction, rolesArr):
    for r in rolesArr:
        if r not in get_role_name(inter.user.roles):
            common.gInvalidCmdMsg = "You don't have privilege to access this command"
            return False
    return True


def check_channels(inter: discord.Interaction, channelsArr):
    if not inter.channel.id in channelsArr:
        common.gInvalidCmdMsg = "Invalid Channel"
        return False
    return True


# Returns a message (is it good architecture?)
# NOTE:Invalid USER and ITEM parameters arent handled here should be handled where the function is called!!
def buy(user_id, item_name, quantity):
    item_price = common.DB.get_item_price(item_name)
    item_quantity = common.DB.get_item_quantity(item_name)
    balance = common.DB.get_balance_by_id(user_id)
    # handling invalid quantity
    if quantity == 0:
        return "Your request went from where you are through the complex network of internet just to buy nothing? What a shame..."
    if quantity <= 0:
        return "Two things can't be negative: a mass, and the quantity you would buy here..."
    # handling shortage
    if item_quantity <= 0:
        return f"Sorry, no more {item_name} in the storage, try something else (if available)."
    diff = item_quantity - quantity
    if diff < 0:
        return f"You can't buy an amount of {quantity}, only {item_quantity} of {item_name} is available."
    # balance check
    total_price = quantity * item_price
    if total_price > balance:
        return "You don't have enough coins for this transaction, you can refill your account when contacting admins"
    # computing the transaction
    common.DB.update_balance_by_id(-total_price, user_id)  # Wildric NOTE: I don't like id being the second argument
    common.DB.update_quantity_by_name(item_quantity - quantity, item_name)
    newBalance = common.DB.get_balance_by_id(user_id)

    transaction_time = datetime.datetime.now()
    common.DB.insert_buy(transaction_time, user_id, balance, newBalance, item_name, item_quantity - quantity,
                         item_quantity, quantity, item_price)
    return f"The transaction was successful, you are left with {newBalance} " + n_coin + ". Enjoy your snack :)"


def get_balance(id_author, id):
    s = ""
    if id == id_author:
        s = "You have " + str(common.DB.get_balance_by_id(id_author)) + " " + n_coin
    else:
        s = str(common.DB.get_user_name_by_id(id)) + " has " + str(common.DB.get_balance_by_id(id)) + " " + n_coin
    return s


# -------------------------------------------------
# Cmds in order, "z" prefix is reserved to cmds accessible only to administrators, such prefix is used for discord command sorting which is alphabetical
# -hello
# -info
# -ff
# -items
# -item
# -user
# -wallet
# -zwallet
# -zbuy
# -zuser
# -zitem
# -zdelete_user
# -zdelete_item


# Commands in order:
@bot.tree.command(name="hello", description="Say hello to FridgeFund", guild=discord.Object(id=common.SERVER_ID))
# @bot.app_commands.describe(sentence="")
async def helloCmd(inter: discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    await inter.response.send_message(embed=create_embed(None, "Hey there!"))


@bot.tree.command(name="info", description="Responds with infos about FridgeFund",
                  guild=discord.Object(id=common.SERVER_ID))
async def infoCmd(inter: discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    await inter.response.send_message(embed=create_embed(None,
                                                         "I'm FridgeFund, a bot that manages NPC fridge; type / and look at different commands in discord"))


# TODO::Find a way to format this; tried space counting formatting but won't work since letters aren't same length
@bot.tree.command(name="ff", description="Lists all users in the database", guild=discord.Object(id=common.SERVER_ID))
async def listCmd(inter: discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    data = common.DB.get_all_users()
    title = None
    msg = ""
    if not data:
        msg += "No user is registered"
    else:
        title = "Ranking of FridgeFunders"
        for user in data:
            msg += "```"
            msg += "Nickname: " + user[1] + " ‎" * 4
            msg += "RealName: " + user[2] + " ‎" * 4
            msg += "Balance: " + str(user[3]) + n_coin + "```"
    await inter.response.send_message(embed=create_embed(title, msg))


@bot.tree.command(name="items", description="Lists all available items", guild=discord.Object(id=common.SERVER_ID))
async def itemsCmd(inter: discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    data = common.DB.get_all_items()
    msg = ""
    title = None
    if not data:
        msg += "No snack is available; the fridge is empty!"
    else:
        title = "Available Snacks"
        for snack in data:
            msg += "```"
            msg += snack[0] + " ‎" * 4
            msg += "Quantity: " + str(snack[1]) + " ‎" * 4
            msg += "Price: " + str(snack[2]) + n_coin + "```"
    await inter.response.send_message(embed=create_embed(title, msg))


@bot.tree.command(name="item", description="Responds with info about specific item given as parameter",
                  guild=discord.Object(id=common.SERVER_ID))
@bot.app_commands.describe(item="The name of the item you're looking for")
async def itemCmd(inter: discord.Interaction, item: str):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    item = item.lower().strip()
    msg = "That snack isn't available, try ```/items``` to see all available snacks"
    if common.DB.item_exist_by_name(item):
        name, quantity, price = common.DB.get_item_by_name(item)
        msg = "```"
        msg += name + " ‎" * 4
        msg += "Quantity: " + str(quantity) + " ‎" * 4
        msg += "Price: " + str(price) + n_coin + "```"
    await inter.response.send_message(embed=create_embed(item, msg))


@bot.tree.command(name="wallet", description="Responds with details about your wallet",
                  guild=discord.Object(id=common.SERVER_ID))
async def walletCmd(inter: discord.Interaction):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    await inter.response.send_message(embed=create_embed("Wallet", get_balance(inter.user.id, inter.user.id)))


@bot.tree.command(name="buy", description="Buy a certain quantity from certain snack",
                  guild=discord.Object(id=common.SERVER_ID))
@bot.app_commands.describe(item="The name of the item you will buy")
@bot.app_commands.describe(quantity="The amount you will buy")
async def buyCmd(inter: discord.Interaction, item: str, quantity: int = 1):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, []):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    # maybe add here user addition if you don't want to do it manually
    if not common.DB.user_exist_by_id(inter.user.id):
        return await inter.response.send_message(
            embed=create_embed(None, "You aren't yet a FridgeFunder, contact admins to become one!"))
    item = item.lower().strip()
    if not common.DB.item_exist_by_name(item):
        return await inter.response.send_message(embed=create_embed(None, "That snack isn't available :("))
    return await inter.response.send_message(embed=create_embed("Transaction", buy(inter.user.id, item, quantity)))


# ********************************BUREAU COMMANDS********************************


@bot.tree.command(name="zwallet", description="admin: Responds with details about wallet of certain user",
                  guild=discord.Object(id=common.SERVER_ID))
async def zwalletCmd(inter: discord.Interaction, user: discord.Member):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    await inter.response.send_message(embed=create_embed(f"{user.name} Wallet", get_balance(inter.user.id, user.id)))


@bot.tree.command(name="zbuy", description="admin: Buy an item for a certain user",
                  guild=discord.Object(id=common.SERVER_ID))
@bot.app_commands.describe(user="The funder who wants to buy")
@bot.app_commands.describe(item="The item to buy")
@bot.app_commands.describe(quantity="The amount to buy")
async def zbuyCmd(inter: discord.Interaction, user: discord.Member, item: str, quantity: int):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if not common.DB.user_exist_by_id(user.id):
        return await inter.response.send_message(embed=create_embed(None, "That user isn't yet a FridgeFunder."))
    item = item.lower().strip()
    if not common.DB.item_exist_by_name(item):
        return await inter.response.send_message(embed=create_embed(None, "That snack isn't available :("))
    await inter.response.send_message(embed=create_embed("Admin Transaction ", buy(user.id, item, quantity)))


@bot.tree.command(name="zuser", description="admin: Create user if not created or update him",
                  guild=discord.Object(id=common.SERVER_ID))
@bot.app_commands.describe(user="The user to update")
@bot.app_commands.describe(balance="The amount to add or substract, can be positive or negative!")
@bot.app_commands.describe(first_name="Real first name of the user")
async def zuserCmd(inter: discord.Interaction, user: discord.Member, balance: float = 0.0, first_name: str = ""):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    transaction_time = datetime.datetime.now()
    # User creation
    first_name = first_name.lower().strip()
    if not common.DB.user_exist_by_id(user.id):
        common.DB.insert_user(user.id, user.name, first_name, 0)
        common.DB.insert_balance(transaction_time, user.id, 0, balance)
        common.DB.update_balance_by_id(balance, user.id)
        await inter.response.send_message(
            embed=create_embed("Database Info", f"The user has been added to the database."))
        return
    # Updating balance and real name
    if first_name != "":
        common.DB.update_realname_by_id(first_name, user.id)
    old_balance = common.DB.get_balance_by_id(user.id)
    common.DB.insert_balance(transaction_time, user.id, old_balance, old_balance + balance)
    common.DB.update_balance_by_id(balance, user.id)
    await inter.response.send_message(embed=create_embed("Database Info", f"The Database has been updated."))


@bot.tree.command(name="zitem", description="admin: Create or update an item",
                  guild=discord.Object(id=common.SERVER_ID))
@bot.app_commands.describe(item="The item to add or update")
@bot.app_commands.describe(price="The price of the item, -1 does not update it!")
@bot.app_commands.describe(quantity="The quantity of the item, -1 does not update it!")
async def zitemCmd(inter: discord.Interaction, item: str, price: float = -1.0, quantity: int = -1):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    item = item.lower().strip()
    if not common.DB.item_exist_by_name(item):
        if price == -1 or quantity == -1:
            return await inter.response.send_message(embed=create_embed("Storage",
                                                                        "You need to set quantity and price if you add the item for the first time!"))
        common.DB.insert_item(item, quantity, price)
        return await inter.response.send_message(embed=create_embed("Storage Info", "Item added!"))

    # No update getting just info
    if price == -1 and quantity == -1:
        name, quantity, price = common.DB.get_item_by_name(item)
        msg = "```"
        msg += name + " ‎" * 4
        msg += "Quantity: " + str(quantity) + " ‎" * 4
        msg += "Price: " + str(price) + n_coin + "```"
        return await inter.response.send_message(embed=create_embed(item, msg))
    # updating the item
    transaction_time = datetime.datetime.now()
    if price != -1:
        common.DB.insert_item_price(transaction_time, item, price, common.DB.get_item_price(item))
        common.DB.update_price_by_name(price, item)
    if quantity != -1:
        common.DB.insert_item_quantity(transaction_time, item, quantity, common.DB.get_item_quantity(item))
        common.DB.update_quantity_by_name(quantity, item)
    return await inter.response.send_message(embed=create_embed("Storage Update", f"{item} has been updated"))


@bot.tree.command(name="zdelete_user", description="admin: Delete a user", guild=discord.Object(id=common.SERVER_ID))
@bot.app_commands.describe(user="The user to delete")
async def zdelete_userCmd(inter: discord.Interaction, user: discord.Member):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    if not common.DB.user_exist_by_id(user.id):
        return await inter.response.send_message(embed=create_embed(None, "This user isn't in the database."))
    common.DB.delete_user_by_id(user.id)
    return await inter.response.send_message(embed=create_embed(None, f"{user.name} is deleted from the database."))


@bot.tree.command(name="zdelete_item", description="admin: Delete an item", guild=discord.Object(id=common.SERVER_ID))
@bot.app_commands.describe(item="The item to delete")
async def bdelete_itemCmd(inter: discord.Interaction, item: str):
    if not check_channels(inter, [common.DEFAULT_CHANNEL_ID]) or not check_roles(inter, ["Bureau"]):
        return await inter.response.send_message(embed=create_embed(None, common.gInvalidCmdMsg))
    item = item.lower().strip()
    if not common.DB.item_exist_by_name(item):
        return await inter.response.send_message(embed=create_embed(None, "This item isn't in the database."))
    common.DB.delete_item_by_name(item)
    return await inter.response.send_message(embed=create_embed(None, f"{item} is deleted from the database."))






