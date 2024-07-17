from pyrogram import Client, filters, idle

channel_id = -1002164329867 #your id

app = Client("my_bot")

@app.on_message(filters.chat(channel_id))
def new_message(client, message):
    print(message.text)

app.run()
