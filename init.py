
from pyrogram import Client, filters
from config import api_id, api_hash

api_id
api_hash

app = Client(name='my_account', api_id=api_id, api_hash=api_hash)

@app.on_message(filters.text)
async def echo(Client, message):
    await message.reply(message.text)



print("\n[+] Bot Started!\n[+] Press Ctrl+C to stop the bot.")
app.start()


