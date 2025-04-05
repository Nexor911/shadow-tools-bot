import telebot;
bot = telebot.TeleBot('Bot-token')
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/tools":
        bot.send_message(message.from_user.id, "https://osintframework.com/, https://inteltechniques.com/, https://www.shodan.io/, https://leakcheck.io/, https://www.tineye.com/")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "доступна только команда /tools")
    else:
        bot.send_message(message.from_user.id, "напиши /help")
        
bot.polling(none_stop=True, interval=0)
    
