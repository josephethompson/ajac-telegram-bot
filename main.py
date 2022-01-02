import configparser
import json
import random
import time
import threading

from telethon import TelegramClient, events
from telethon.tl.types import InputMessagesFilterPhotos
from telethon.tl.types import MessageEntityMention
from telethon.tl.types import MessageEntityMentionName

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = str(config['Telegram']['api_hash'])
bot_token = str(config['Telegram']['bot_token'])

# Get user data
user_data_file = open('Storage/userdata.json', 'r')
all_user_data = json.load(user_data_file)

#other variables
PhysiqueFridayTag = "#FizeekFriday"
BotResponses = ["GOOD JOB BROTHER", "WELL DONE", "WOOOO", "I SEE YOU!", "GAINNNS", "HYPERBOREAN"]

bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

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

async def get_last_physique_post(user_id, chat):
    user_data = get_user_data(user_id) or create_user_data(user_id)
    last_physique_post_id = user_data['lastPhysiqueFridayPostId']
    if last_physique_post_id != None:
        message = await bot.get_messages(chat, ids=last_physique_post_id )
        return message

@bot.on(events.NewMessage)
async def my_event_handler(event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    sender_user_data = get_user_data(sender.id) or create_user_data(sender.id)

    if PhysiqueFridayTag.lower() in event.raw_text.lower() and event.photo:
        sender_user_data['lastPhysiqueFridayPostId'] = event.message.id
        await event.reply(random.choice(BotResponses))
    elif "/fizeekcheck" in event.raw_text.lower():
        users = await bot.get_participants(chat)
        message = event.message
        entities = message.entities

        for entity in entities:
            if entity.__class__ is MessageEntityMention:
                mentioned_user_name = event.raw_text[entity.offset+1:len(event.raw_text)]
                mentioned_user = get_user_from_username(mentioned_user_name, users)
                last_physique_post = await get_last_physique_post(mentioned_user.id, chat)
                if last_physique_post != None:
                    await event.reply(f'{mentioned_user.username or mentioned_user.first_name} FIZEEK CHECK: \n\nLAST FIZEEK POST DATE:  {last_physique_post.date.strftime("%B %d, %Y")}\nLAST FIZEEK POST:')
                    await bot.send_message(chat, last_physique_post)
                else:
                    await event.reply('NO FIZEEK FOUND')
            elif entity.__class__ is MessageEntityMentionName:
                last_physique_post = await get_last_physique_post(entity.user_id, chat)
                if last_physique_post != None:
                    await event.reply(f'{mentioned_user.username or mentioned_user.first_name} FIZEEK CHECK: \n\nLAST FIZEEK POST DATE:  {last_physique_post.date.strftime("%B %d, %Y")}\nLAST FIZEEK POST:')
                    await bot.send_message(chat, last_physique_post)
                else:
                    await event.reply('NO FIZEEK FOUND')
def main_update():
    while True:
        time.sleep(5)

        try:
            with open("Storage/userdata.json", "w") as outfile:
                json.dump(all_user_data, outfile)
        except:
            pass

threading.Thread(target=main_update).start()
bot.run_until_disconnected()
