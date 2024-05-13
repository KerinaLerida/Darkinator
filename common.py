import os

BOT_TOKEN = os.environ.get('BOT_TOKEN', 'TOKEN')
SERVER_ID = int(os.environ.get('SERVER_ID', 0))
DEFAULT_CHANNEL_ID = int(os.environ.get('DEFAULT_CHANNEL_ID', 0))
ADMIN_ROLE = os.environ.get('ADMIN_ROLE', "role_admin")

#DONT EDIT THE FOLLOWING!
gInvalidCmdMsg = "Hmm, weird bug; if you see this msg contact the developper"
gDB            = None #global database


#from os import get_env as getenv
