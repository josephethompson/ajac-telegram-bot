import configparser
import json
import random
import time
import threading

from telethon import TelegramClient, events
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.tl.types import MessageEntityMention
from telethon.tl.types import MessageEntityMentionName

config = configparser.ConfigParser()
config.read("/home/joseph_ethompson01/ajac-telegram-bot/config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = str(config['Telegram']['api_hash'])
bot_token = str(config['Telegram']['bot_token'])

# Get user data
user_data_file = open('/home/joseph_ethompson01/ajac-telegram-bot/Storage/userdata.json', 'r')
all_user_data = json.load(user_data_file)

#other variables
PhysiqueCheckCommands = ["/fizeekcheck", "/physiquecheck"]
PhysiqueFridayTags = ["FizeekFriday", "PhysiqueFriday", "Fizeek Friday", "Physique Friday", "PhysiquePost", "FizeekPost", "Fizeek Post", "Physique Post"]
BotResponses = ["GOOD JOB BROTHER", "WELL DONE", "WOOOO", "I SEE YOU", "GAINNNS", "HYPERBOREAN", "CHADISTANIAN"]

bot = TelegramClient('bot1', api_id, api_hash).start(bot_token=bot_token)

def create_user_data(user_id):
    user_key = str(user_id)
    all_user_data[user_key] = {
        'lastPhysiqueFridayPostId': None,
    }

    return all_user_data[user_key]

def get_user_data(user_id):
    user_key = str(user_id)

    if user_key in all_user_data:
        return all_user_data[user_key]

def get_user_from_username(user_name, users):
    for user in users:
        if user.username == user_name:
            return user

def get_user_from_userid(user_id, users):
    for user in users:
        if user.id == user_id:
            return user

async def get_last_physique_post(user_id, chat):
    user_data = get_user_data(user_id) or create_user_data(user_id)
    last_physique_post_id = user_data['lastPhysiqueFridayPostId']
    if last_physique_post_id != None:
        message = await bot.get_messages(chat, ids=last_physique_post_id )
        return message

async def check_physique(user, event):
    chat = await event.get_chat()
    last_physique_post = await get_last_physique_post(user.id, chat)
    if last_physique_post != None:
        await event.reply(f'{user.username or user.first_name} FIZEEK CHECK: \n\nLAST FIZEEK POST DATE:  {last_physique_post.date.strftime("%B %d, %Y")}\nLAST FIZEEK POST:')
        await bot.send_message(chat, last_physique_post)
    else:
        await event.reply('NO FIZEEK FOUND')

@bot.on(events.NewMessage)
async def my_event_handler(event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    sender_user_data = get_user_data(sender.id) or create_user_data(sender.id)

    if "/help" in event.raw_text.lower():
        await event.reply("COMMAND LIST: \n\n/physiquecheck [user] (/fizeekcheck [user])")
    elif any(tag.lower() in event.raw_text.lower() for tag in PhysiqueFridayTags) and event.photo:
        sender_user_data['lastPhysiqueFridayPostId'] = event.message.id
        await event.reply(random.choice(BotResponses))
    elif any(tag.lower() in event.raw_text.lower() for tag in PhysiqueCheckCommands):
        users = await bot.get_participants(chat)
        message = event.message
        entities = message.entities

        mentioned_user = sender
        for entity in entities:
            if entity.__class__ is MessageEntityMention:
                mentioned_user_name = event.raw_text[entity.offset+1:len(event.raw_text)]
                mentioned_user = get_user_from_username(mentioned_user_name, users)
            elif entity.__class__ is MessageEntityMentionName:
                mentioned_user = get_user_from_userid(entity.user_id, users)

        await check_physique(mentioned_user, event)

def main_update():
    while True:
        time.sleep(5)

        try:
            with open("/home/joseph_ethompson01/ajac-telegram-bot/Storage/userdata.json", "w") as outfile:
                json.dump(all_user_data, outfile)
        except:
            pass

threading.Thread(target=main_update).start()
bot.run_until_disconnected()
