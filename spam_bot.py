# import the necessary modules
from datetime import datetime
from http import client
import time
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
import os
import asyncio
from config import CHAT_ID
from helper.words import thousand_words as sp
import sys
from helper.functions import eta_converter, json_io


# load variables from config.py
if os.path.exists("config.py"):
    from config import (
        API_ID,
        API_HASH,
        USER_ID,
        # CHAT_ID,
    )
else:
    sys.exit('config.py does not exist. Exiting...')


# initiate the client object
app:Client = Client(name="my_account", api_id=API_ID, api_hash=API_HASH)


# load previous informatioin from infos.json
prev_infos = json_io(mode='r')

# commands and prefixes
start_command_list = ['sp', 'spam']
stop_command_list = ['st', 'stop', 'pause']
status_command_list = ['stat', 'stats', 'status']
continue_command_list = ['ct', 'cont', 'continue']
reset_command_list = ['reset', 'clear', 'cl', 'clean']
command_prefixes_list = ['.', '/', '!']



##################### Starting the bot ###########################
# @app.on_message(filters.command(start_command_list, prefixes=command_prefixes_list))
async def startCommand(app:Client, message:Message, word_list=sp, cont=False):

    default_msgnum: int = 20
    userId = message.from_user.id
    chatId = message.chat.id
    txt:str = message.text
    command_msg: int = message.id
    userName = message.from_user.username
    name: str = str(message.from_user.first_name)

    if userId != int(USER_ID):
        unauthorized_user = await app.send_message(chatId, "Only @Shadoworbs can start a task.", reply_to_message_id=message.id)
        print(f"\nAnauthorized user report\nUsername: {userName}\nUserId: {userId}\nName: {name}")
        await asyncio.sleep(5000)
        await unauthorized_user.delete()
    else:
        # load previous information 
        global prev_infos
        # create a new infos dict to temporarily hold informatiion
        infos = dict()
        # check if the last task was completed
        try:
            if 'messages_left' and 'Done' in prev_infos.keys():
                if prev_infos['messages_left'] > 0 and prev_infos['Done'] is not True and cont is False:
                    await message.delete()
                    await app.send_message(chatId, 'The last task did not complete. \nUse /continue to resume.')
                    print('Last task did not complete.')
                    return
        except Exception as i:
            print(f'Error occured in checking if last task was completed\n{i}')
            pass
        # if continue is false
        if cont is not True:
            msg_num = int(txt.split(' ')[1]) if len(txt.split(' ')) > 1 else 20
            word_list = sp[:msg_num]

        # if the command is to continue
        else:
            msg_num = prev_infos['messages_left']
            mleft = prev_infos["messages_left"]
            msent = prev_infos["messages_sent"]
            msg_num = prev_infos['total_messages']
            word_list = sp[msent:msg_num]


        # send a reply
        if not cont:
            status_msg = await message.reply("Yes sir 🫡\n**Initiating Violence Mode 😈**")
            # print a message to the console
            print("Task Started!")
        else:
            status_msg = await message.reply("**Continuing Violence Mode**")
            # print a message to the console
            print('Continuing task...\n')

        # messages left
        messages_left = len(word_list)
        # messages sent
        messages_sent = 0
        # estimated time of completion
        eta = messages_left * 10

        # create a new infos dict
        infos["command"] = command_msg
        infos["status_msg_id"] = status_msg.id
        infos["total_messages"] = msg_num
        # set the state to not done
        infos["Done"] = False

        # try to delete previous messages and commands
        if len(prev_infos) > 0:
            msg_ids = ['command', 'start_msg_id', 'random_word_id']
            for id in msg_ids:
                if id not in prev_infos.keys():
                    pass
                else:
                    try:
                        await app.delete_messages(chat_id=chatId, message_ids=prev_infos[id])
                    except Exception as e:
                        print(f'Error in delete_messages()\n{e}')

        try:
            # loop through the list of words in ../spam.py
            for word in word_list:
                await asyncio.sleep(7)
                # check if user replied to a message
                if message.reply_to_message:
                    random_word = await app.send_message(chatId, word, reply_to_message_id=message.reply_to_message.id)
                else:
                    random_word = await app.send_message(chatId, word)
                # update the infos dict
                infos["status_msg_id"] = status_msg.id  
                infos["random_word_id"] = random_word.id

                # save the updated infos into a json file
                json_io(mode='w', infos=infos)
                # delay for 3 seconds
                await asyncio.sleep(1)
                # decrease the number of messages left by 1
                messages_left -= 1
                # decrease the ETA by 10
                eta -= 10
                # increase the number of messages sent by 1
                messages_sent += 1
                # update the messages left and sent values
                infos["messages_left"] = messages_left
                infos["messages_sent"] = messages_sent
                # update eta with new values 
                _, hours, minutes, seconds = eta_converter(eta)
                eta_ = f"{hours}h {minutes}m {seconds}s"
                # edit the reply message with some text
                msg = f"**Total  💬 :** `{len(word_list):,}`"
                msg += f"\n**Sent ✅    :** `{messages_sent:,}`"
                msg += f"\n**Left ♻️    :** `{messages_left:,}`"
                msg += f"\n**ETA ⏳     :** `{eta_}`\n\n"
                msg += f"**Cooked with ❤️ by : @shadoworbs**"
                # update the status message on telelgram
                await status_msg.edit(msg, disable_web_page_preview=True)
                # update the json
                json_io(mode='w', infos=infos)
                # print messages left
                print(f"{messages_left} messages left", end="\r")
                # delay for 1 second
                await asyncio.sleep(2)
                # delete the word sent from the list
                await random_word.delete()
            # print a message to the console after task is completed
            print(f"\nTask Completed. Time: {datetime.now().strftime('%I:%M %p')}")
            # send a complete message
            msg = f"**Vawulence mode ended ✅**\nUse /spam [n] to restart."
            complete = await app.send_message(chatId, msg)
            # change the state to Done
            infos["Done"] = True
            infos['complete_msg_id'] = complete.id
            json_io(mode='w', infos=infos)
            # delete the reply message
            await status_msg.delete()
            # delete the command message
            await message.delete()
            await asyncio.sleep(20)
            await complete.delete()
        except Exception as e1:
            print(F'Error in end of startCommand() \n{e1}')
            # when there is an error in edit message
            # delete the current word sent
            # (may not work because the word may have been deleted already)
            await random_word.delete()
            # clear the infos dict to show no tasks running
            infos["Done"] = True


################################# Get bot task status ###############################
# @app.on_message(filters.command(status_command_list, prefixes=command_prefixes_list))
async def statusCommand(app: Client, message):
    userId = message.from_user.id
    chatId = message.chat.id
    _message = message.text
    mention = message.from_user.mention

    infos = json_io('r')

    # if the user sends the stats command
    if userId == int(USER_ID):
        # print a message to the console
        print(f"\nUsername: @{message.from_user.username} and ID: {message.from_user.id}  requested stats.")
        # if there are tasks running (infos dict is not empty)
        if infos['Done'] is not True and infos['messages_left'] > 0:
            await message.delete()
            # print a message to the console
            print(f"Current task ID: {infos['status_msg_id']}")
            # send a reply
            chat_ = str(chatId)[3:]
            msg = '**Status:** <i>running 🟢</i>\n'
            msg += f"**[🔗 Task link 🔗](https://t.me/c/{chat_}/{infos['status_msg_id']})**"
            task = await app.send_message(chatId, msg, disable_web_page_preview=True)
            # wait for 10 seconds
            await asyncio.sleep(20)
            # delete the reply sent to the user
            await task.delete()

        # if there are no tasks running (infos dict is empty)
        else:
            # print a message to the console
            print("No tasks running!")
            await message.delete()
            # send a reply
            msg = f"**Spam Status:** <i>stopped 🛑</i>"
            msg += f"\nStart a new task with /spam [n]"
            task = await app.send_message(chatId, msg)
            # wait for 5 seconds
            await asyncio.sleep(20)
            # delete the reply
            await task.delete()
    else: #userId != int(USER_ID):
        msg = 'Hahaha, got you 😂😂\n'
        msg += 'Check out my repo and host your own bot on your local maching at no cost.\n'
        msg += '**[Spam Bot Repo](https://github.com/shadoworbs/spam_bot)**\n'
        msg += "Don't forget to fort and star the repo."
        await message.reply(msg, disable_web_page_preview=True)


######################### Stop the bot ############################
# @app.on_message(filters.command(stop_command_list, prefixes=command_prefixes_list))
async def stopCommand(app, message):
    userId = message.from_user.id
    chatId = message.chat.id
    _message = message.text
    mention = message.from_user.mention

    json_items = json_io('r')
    msg_ids = json_items['command'], json_items['status_msg_id'], json_items['random_word_id']


    # if the admin sends the stop command
    if userId == int(USER_ID):
        # print a message to the console
        print("\nTask stopped")
        # send a reply that the bot is stopped
        stopped = await message.reply(f"Vawulence mode stopped.\nUse /spam [n] to restart.")
        # wait for 1 second
        await asyncio.sleep(1)
        # delete the user's message
        await message.delete()
        # wait for 1 second
        await asyncio.sleep(1)
        # delete the reply sent to the user
        await stopped.delete()
        ''' delete the status message to deliberately
            # to cause an error in edit message
            # that's the only way to stop the task, for now. '''
        for id in msg_ids:
            try:
                await app.delete_messages(chatId, id)
            except Exception as e:
                print(f'Error in deletiing messages stop()\n{e}')
                pass
        sys.exit('\nStopping the programm...')


############# Continue ##################
# @app.on_message(filters.command(continue_command_list, prefixes=command_prefixes_list))
async def _continue(app, message):
    global sp
    chatId = message.chat.id
    userId = message.from_user.id

    if userId == int(USER_ID):
        # load previous infos from a json file
        prev_infos = json_io(mode='r')

        Done = prev_infos["Done"]
        mleft = prev_infos["messages_left"]
        msent = prev_infos["messages_sent"]
        msg_num = prev_infos['total_messages']
        word_list_c = sp[msent:msg_num]

        if not Done and mleft > 0:
            print("Continuing from where we left off.")
            await startCommand(app=app, message=message, word_list=word_list_c, cont=True)
        else:
            await message.delete()
            task_done = await app.send_message(chat_id=chatId,
                                            text="No tasks available for continuation!\nUse /spam [n] to start again.")
            await asyncio.sleep(20)
            await task_done.delete()


################################## Clear infos.json ################################
# @app.on_message(filters.command(reset_command_list, prefixes=command_prefixes_list))
async def reset_all_messages(app, message):
    chatId = message.chat.id
    userId = message.from_user.id
    if userId == int(USER_ID):
        infos = dict()
        infos['Done'] = True
        infos['messages_left'] = 0
        infos['messages_sent'] = 0
        json_io(mode='w', infos=infos)
        await asyncio.sleep(2)
        await message.delete()
        await app.send_message(chatId, 'All messages have been cleared!\nUse /spam [n] to start a new task.')
        print('All messages cleared.')



# print date to the console
print(f"\n[+] Bot Started | {datetime.now().strftime('%A %B %d %Y - %I:%M %p')}\n")


# register handlers for the commands
app.add_handler(MessageHandler(startCommand, filters.command(start_command_list, command_prefixes_list)))
app.add_handler(MessageHandler(stopCommand, filters.command(stop_command_list, command_prefixes_list)))
app.add_handler(MessageHandler(statusCommand, filters.command(status_command_list, command_prefixes_list)))
app.add_handler(MessageHandler(reset_all_messages, filters.command(reset_command_list, command_prefixes_list)))
app.add_handler(MessageHandler(_continue, filters.command(continue_command_list, command_prefixes_list)))



# run the bot

if __name__ == '__main__':
    app.run()


# TODO:
# implement code to multi thread the program.
# add reset command to reset messages (for testing purposes)