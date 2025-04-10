import telebot
import requests
import logging

# Токен бота
bot = telebot.TeleBot('Token')

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    filename='logi.log',
    filemode='a',
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

# Логируем старт бота
@bot.message_handler(commands=['start'])
def start_command(message):
    logging.info(f'Пользователь {message.from_user.id} написал /start')
    bot.send_message(message.chat.id, "Hello, say /help")

# Логируем команду /help
@bot.message_handler(commands=['help'])
def help_command(message):
    logging.info(f'Пользователь {message.from_user.id} написал /help')
    bot.send_message(message.chat.id, "Доступные команды:\n/tools\n/ip [ip адрес]")

# Логируем команду /tools
@bot.message_handler(commands=['tools'])
def tools_command(message):
    logging.info(f'Пользователь {message.from_user.id} написал /tools')
    bot.send_message(message.chat.id, "https://osintframework.com/, https://inteltechniques.com/, https://www.shodan.io/, https://leakcheck.io/, https://www.tineye.com/")

# Функция поиска по IP
def ip_lookup(ip):
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url).json()
    if response['status'] == 'fail':
        return "IP не найден!"
    
    result = f"""
IP: {response['query']}
Страна: {response['country']}
Город: {response['city']}
Провайдер: {response['isp']}
Координаты: {response['lat']}, {response['lon']}
"""
    return result

# Логируем команду /ip
@bot.message_handler(commands=['ip'])
def ip_command(message):
    try:
        ip = message.text.split()[1]
        result = ip_lookup(ip)
        logging.info(f'Пользователь {message.from_user.id} сделал IP lookup: {ip}')
        bot.send_message(message.chat.id, result)
    except:
        bot.send_message(message.chat.id, "Использование: /ip [ip адрес]")

# Логируем все остальные сообщения
@bot.message_handler(func=lambda message: True)
def log_all(message):
    logging.info(f'Пользователь {message.from_user.id} написал сообщение: {message.text}')

# Запуск бота
bot.polling(none_stop=True, interval=0)

    
