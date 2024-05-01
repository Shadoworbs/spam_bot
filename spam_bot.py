# import the necessary modules
from datetime import datetime
from pyrogram import Client, filters
import os
import asyncio
from words import thousand_words as sp
import json


# load variables from config.py
if os.path.exists("config.py"):
    from config import (
        api_id,
        api_hash,
        spam_chat_id,
        my_id,
        number_of_messages_to_send,
        message_id_to_reply_to as msg_id,
    )


# decide how many messages to send per task based on variables from config.py
msg_num = number_of_messages_to_send
if (msg_num is not None 
    and int(msg_num) > 0
    and int(msg_num) <= len(sp)
    ):
    msg_num = int(msg_num)
    sp = sp[:msg_num]
else:
    sp = sp[:20]


# initiate the client object
app = Client(name="my_account", api_id=api_id, api_hash=api_hash)


# the infos dictionary
infos = dict()
# the list of completed tasks
completed: list = []


# load previous infos from a json file
if os.path.exists("infos.json"):
    try:
        with open("infos.json", "r") as f:
            prev_infos = json.load(f)
    except:
        pass


# Starting the bot
@app.on_message(filters.command("spam"))
async def startCommand(app, message, sp_=sp):
    userId = message.from_user.id
    chatId = message.chat.id
    _message = message.text
    command_msg: int = message.id

    global infos, msg_num
    global prev_infos

    # inquire_messages_index = await app.send_message(chatId, 'How many messages do you want to send?')

    # if the message is sent in the specified chat and by the specified user and is the start command
    if chatId == int(spam_chat_id) and userId == int(my_id):
        # send a reply
        status_msg = await message.reply("Yes sir 🫡\nInitiating **Violence Mode 😈**")
        # print a message to the console
        print("Task Started!")
        # messages left
        messages_left = len(sp_)
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
            try:
                await app.delete_messages(
                    chatId,
                    [
                        prev_infos["msg_id"],
                        prev_infos["command"],
                        prev_infos["status_msg_id"],
                    ],
                )
            except:
                pass
        try:
            # loop through the list of words in ../spam.py
            for word in sp_:
                # send one word from the list as a reply to the message ID provided
                if msg_id and msg_id is not None and msg_id > 0:
                    # delay for 7 seconds
                    await asyncio.sleep(7)
                    random_word = await app.send_message(
                        chatId, word, reply_to_message_id=msg_id
                    )
                # else, don't reply to any message.
                else:
                    random_word = await app.send_message(chatId, word)
                # update the infos dict
                infos["status_msg_id"] = status_msg.id
                infos["random_word_id"] = random_word.id

                # save the updated infos into a json file
                with open("infos.json", "w") as f:
                    json.dump(infos, f, indent=3)
                # delay for 3 seconds
                await asyncio.sleep(2)
                # decrease the number of messages left by 1
                messages_left -= 1
                # decrease the ETA by 10
                eta -= 10
                # increase the number of messages sent by 1
                messages_sent += 1
                # update the messages left and sent values
                infos["messages_left"] = messages_left
                infos["messages_sent"] = messages_sent
                # change seconds to (hours, minutes and seconds)
                seconds: int = eta
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                days, hours = divmod(hours, 24)
                eta_ = f"{hours}h {minutes}m {seconds}s"
                # edit the reply message with some text
                msg = f"**Total  💬 :** `{len(sp_):,}`"
                msg += f"\n**Sent ✅    :** `{messages_sent:,}`"
                msg += f"\n**Left ♻️    :** `{messages_left:,}`"
                msg += f"\n**ETA ⏳     :** `{eta_}`\n\n"
                msg += f"**Cooked with ❤️ by : @shadoworbs**"
                await status_msg.edit(msg, disable_web_page_preview=True)
                # print messages left
                print(f"{messages_left} messages left", end="\r")
                # delay for 1 second
                await asyncio.sleep(1)
                # delete the word sent from the list
                await random_word.delete()
            # append 1 to the completed list (to show how many times the task has been completed)
            completed.append("1")
            # print a message to the console
            print(f"Task Completed {len(completed)} times. | Time: {datetime.now().strftime('%I:%M %p')}")
            # send a complete message
            msg = f"**Task completed ✅**"
            msg += f"\n**Messages sent💬:** <code>{len(sp) * len(completed)}</code>✨"
            complete = await app.send_message(chatId, msg)
            # change the state to Done
            infos["Done"] = True
            # save the updated infos into a json file
            with open("infos.json", "w") as f:
                json.dump(infos, f, indent=3)
            # delete the reply message
            await status_msg.delete()
            # delete the command message
            await message.delete()
            await asyncio.sleep(20)
            await complete.delete()
        except Exception as e:
            print(e)
            # when there is an error in edit message
            # delete the current word sent
            # (may not work because the word may have been deleted already)
            await random_word.delete()
            # clear the infos dict to show no tasks running
            infos["Done"] = True


# Get bot task status
@app.on_message(filters.command("stats"))
async def statusCommand(app, message):
    userId = message.from_user.id
    chatId = message.chat.id
    _message = message.text
    mention = message.from_user.mention

    global infos

    # if the user sends the stats command
    if userId == int(my_id) and chatId == int(spam_chat_id):
        # print a message to the console
        print(f"\nUser  {message.from_user.id}  requested stats.")
        # if there are tasks running (infos dict is not empty)
        if ("Done" in infos.keys()
            and infos['Done'] == False
            ):
            await message.delete()
            # print a message to the console
            print(f"Current task ID: {infos['status_msg_id']}")
            # send a reply
            chat_ = spam_chat_id[3:]
            msg = f"**[Current task ID ✍️](https://t.me/c/{chat_}/{infos['status_msg_id']})**"
            task = await app.send_message(chatId, msg, disable_web_page_preview=True)
            # wait for 10 seconds
            await asyncio.sleep(10)
            # delete the reply sent to the user
            await task.delete()

        # if there are no tasks running (infos dict is empty)
        else:
            # print a message to the console
            print("No tasks running!")
            await message.delete()
            # send a reply
            msg = f"**No tasks running!**"
            task = await message.reply(msg)
            # wait for 5 seconds
            await asyncio.sleep(5)
            # delete the reply
            await task.delete()


# Stop the bot
@app.on_message(filters.command("stop"))
async def stopCommand(app, message):
    userId = message.from_user.id
    chatId = message.chat.id
    _message = message.text
    mention = message.from_user.mention
    # access the global scope
    global infos
    # set the status to done
    # infos["Done"] = True
    # if the admin sends the stop command
    if userId == int(my_id) and chatId == int(spam_chat_id):
        # print a message to the console
        print("\nTask stopped")
        # send a reply that the bot is stopped
        stopped = await message.reply(f"Bot Stopped by **{mention}**")
        # wait for 1 second
        await asyncio.sleep(1)
        # delete the user's message
        await message.delete()
        # wait for 1 second
        await asyncio.sleep(1)
        # delete the reply sent to the user
        await stopped.delete()
        try:
            # delete the reply message to deliberately
            # to cause an error in edit message
            # that's the only way to stop the task
            await app.delete_messages(chatId, infos["status_msg_id"])
        except:
            pass
        try:
            await app.delete_messages(chatId, infos["command"])
        except:
            pass


############# Continue ##################
@app.on_message(filters.command("continue"))
async def _continue(app, message):
    global sp, msg_num
    chatId = message.chat.id

    # load previous infos from a json file
    if os.path.exists("infos.json"):
        try:
            with open("infos.json", "r") as f:
                prev_infos = json.load(f)
        except Exception as e:
            print(e)
            pass

    Done = prev_infos["Done"]
    mleft = prev_infos["messages_left"]
    msent = prev_infos["messages_sent"]
    _sp = sp[msent:msg_num]

    if not Done and mleft > 0:
        print("Continuing from where we left off.")
        await startCommand(app=app, message=message, sp_=_sp)
    else:
        # await startCommand(app=app, message=message, sp_=sp)
        task_done = await app.send_message(chat_id=chatId, 
                               text="The last task was done!\nUse /spam to start again.")
        await asyncio.sleep(10)
        await task_done.delete()
     

print(f"\n[+] Bot Started | {datetime.now().strftime('%A %B %d %Y - %I:%M %p')}\n")

app.run()


# TODO:
#
