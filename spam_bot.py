# import the necessary modules
from datetime import datetime
from pyrogram import Client, filters
from dotenv import load_dotenv
import os
import asyncio
from words import thousand_words as sp


try:
    # load the environment variables
    load_dotenv()
    api_id = os.getenv("api_id")
    api_hash = os.getenv("api_hash")
    bot_token = os.getenv("bot_token")
    spam_chat_id: int = os.getenv("spam_chat_id")
    my_id: int = os.getenv("my_id")
    msg_num = os.getenv("number_of_messages_to_send")
except:
    # load variables from config.py
    from config import (api_id, 
                        api_hash,
                        spam_chat_id,
                        my_id, 
                        msg_num)


# decide how many messages to send per task based on variables from config.py
if (msg_num is not None
    and msg_num.isdigit()
    and int(msg_num) > 0
    and int(msg_num) <= len(sp)
    ):
    msg_num = int(msg_num)
    sp = sp[:msg_num]
else:
    sp = sp[:20]


# initiate the client object
app = Client(name='my_account', api_id=api_id, api_hash=api_hash)


# the infos dictionary
infos = dict()
# the list of completed tasks
completed: list = []


# Starting the bot
@app.on_message(filters.text, filters.group)
async def startCommand(app, message):
    global infos
    # if the message is sent in the specified chat and by the specified user and is the start command
    if (message.chat.id == int(spam_chat_id) 
        and message.from_user.id == int(my_id)
        and message.text == "/start@spam_bot"):
        # send a reply
        reply = await message.reply("Yes sir 🫡")
        # print a message to the console
        print("Task Started!")
        # messages left
        messages_left = len(sp)
        # messages sent
        messages_sent = 0
        # estimated time of completion
        eta = messages_left * 10

        try:
            # loop through the list of words in ../spam.py
            for word in sp:
                # delay for 7 seconds
                await asyncio.sleep(7)
                # send one word from the list
                repl = await app.send_message(spam_chat_id, 
                                              word, 
                                              reply_to_message_id=message.id)
                # delay for 3 seconds
                await asyncio.sleep(2)
                # decrease the number of messages left by 1
                messages_left -= 1
                # decrease the ETA by 10
                eta -= 10
                # increase the number of messages sent by 1
                messages_sent += 1
                # change seconds to (hours, minutes and seconds)
                seconds: int = eta
                minutes, seconds = divmod(seconds, 60)
                hours, minutes = divmod(minutes, 60)
                days, hours = divmod(hours, 24)
                eta_ = f"{hours}h {minutes}m {seconds}s"
                # create an updated infos dict
                updated_infos = {"messages_left": messages_left,
                                 "messages_sent": messages_sent,
                                 "reply": reply.id}
                # update the infos dict the newly created dict
                infos.update(updated_infos)
                # edit the reply message with some text
                msg = f"**Total messages 💬:** `{len(sp):,}`"
                msg += f"\n**Messages sent 💬:** `{messages_sent:,}`"
                msg += f"\n**Messages left 💬:** `{messages_left:,}`"
                msg += f"\n**Time left ⏳:** `{eta_}`"
                msg += f"\n**Made with ❤️ by:** @shadoworbs"
                await reply.edit(msg, disable_web_page_preview=True)
                # print messages left
                print(f'{messages_left} messages left', end='\r')
                # delay for 1 second
                await asyncio.sleep(1)
                # delete the word sent from the list
                await repl.delete()
            # append 1 to the completed list (to show how many times the task has been completed)
            completed.append("1")
            # print a message to the console
            print(f'Task Completed {len(completed)} times')
            # send a complete message
            msg = f"**Task completed ✅**"
            msg += f"\n**By:** {message.from_user.mention}"
            msg += f"\n**Total messages sent💬:** `{len(sp) * len(completed)}`✨"
            await app.send_message(spam_chat_id, msg)
            # delete the reply message
            await reply.delete()
            # delete the command message
            await message.delete()
            # stop the progress bar
            # bar.finish()
        except Exception as e:
            print(e)
            # when there is an error in edit message
            # delete the current word sent
            # (may not work because the word may have been deleted already)
            await repl.delete()
            # clear the infos dict to show no tasks running
            infos.clear()
            # return the function and start listening for a new command
            return
        
    # if the user is not me and the message is sent in the specified chat
    if (message.from_user.id != int(my_id) 
          and message.chat.id == int(spam_chat_id)
          and message.text == "/start@spam_bot"
          ):
        # send a reply to the user
        msg = await app.send_message(spam_chat_id,
                                     f"Hey {message.from_user.mention}\nSorry, you can't start me 🤭.",
                                     reply_to_message_id=message.id)
        # wait for 10 seconds
        await asyncio.sleep(10)
        # delete the reply sent to the user
        await msg.delete()


# Get bot task status
@app.on_message(filters.command('stats'), filters.group)
async def statusCommand(app, message):
    global infos
    # if the user sends the stats command
    if message.from_user.id == int(my_id) and message.chat.id == int(spam_chat_id):
        # if there are tasks running (infos dict is not empty)
        if len(infos) > 0 and infos["messages_left"] > 0 :
            await message.delete()
            # print a message to the console
            print(f"Current task ID: {infos['reply']}")
            # send a reply
            task = await app.send_message(spam_chat_id, 
                                          f"**[Current task ID ✍️]{infos['reply']})**",
                                          reply_to_message_id=infos["reply"],
                                          disable_web_page_preview=True)
            # wait for 10 seconds
            await asyncio.sleep(30)
            # delete the reply sent to the user
            await task.delete()

        # if there are no tasks running (infos dict is empty)
        else:
            # print a message to the console
            print("\nNo tasks running!")
            await message.delete()
            # send a reply
            task_ = await message.reply("No tasks running!")
            # wait for 5 seconds
            await asyncio.sleep(5)
            # delete the reply
            await task_.delete()
        # stop the function and start listening for a new command

    # if the user is not me and the message is sent in the specified chat
    if (message.from_user.id != int(my_id) 
          and message.chat.id == int(spam_chat_id) 
          and message.text == "/stats"
          ):
        # send a reply to the user
        msg = f"Hey {message.from_user.mention}\nSorry, you can't see my stats 📈."
        msg_ = await message.reply(msg)
        # delete the reply sent to the user
        await msg_.delete()


# Stop the bot
@app.on_message(filters.text, filters.group)
async def stopCommand(app, message):
    global infos
    # if the admin sends the stop command
    if (message.from_user.id == int(my_id) 
        and message.chat.id == int(spam_chat_id)
        and message.text == "/stop@spam_bot"):
        # print a message to the console
        print("\nTask stopped")
        # send a reply that the bot is stopped
        stopped = await message.reply(f"Bot Stopped by {message.from_user.mention}")
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
            await app.delete_messages(spam_chat_id, infos["reply"])
        except:
            pass
        return

    # if the user is not me and the message is sent in the specified chat
    elif message.from_user.id != int(my_id) and message.chat.id == int(spam_chat_id) and '/stop@spam_bot' in message.text:
        # delete the user's message
        await message.delete()
        # send a reply to the user
        msg = await app.send_message(spam_chat_id,
                                     f"Hey {message.from_user.mention}\nSorry, you can't stop me 🤭.")
        # wait for 5 seconds
        await asyncio.sleep(5)
        # delete the reply sent to the user
        await msg.delete()
    # stop the function and start listening for a new command
    return


print("\nBot Started at " + datetime.now().strftime("%H:%M:%S"))
app.run()




# todo:
# create a file to store the task id
# create a file to store the reply id and finished message id


