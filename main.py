import telebot
import requests
import logging
from PIL import Image
from PIL.ExifTags import TAGS
import os

bot = telebot.TeleBot('Token-Bot') #вставь токен

# Флаг ожидания фото
user_waiting_photo = {}

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    filename='logi.log',
    filemode='a',
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

@bot.message_handler(commands=['start'])
def start_command(message):
    logging.info(f'Пользователь {message.from_user.id} написал /start')
    bot.send_message(message.chat.id, "Сап, напиши /help")

@bot.message_handler(commands=['help'])
def help_command(message):
    logging.info(f'Пользователь {message.from_user.id} написал /help')
    bot.send_message(message.chat.id, "Доступные команды:\n/tools\n/ip [ip адрес]\n/metadata")

@bot.message_handler(commands=['tools'])
def tools_command(message):
    logging.info(f'Пользователь {message.from_user.id} написал /tools')
    bot.send_message(message.chat.id, "https://osintframework.com/, https://inteltechniques.com/, https://www.shodan.io/, https://leakcheck.io/, https://www.tineye.com/")

@bot.message_handler(commands=['ip'])
def ip_command(message):
    try:
        ip = message.text.split()[1]
        result = ip_lookup(ip)
        logging.info(f'Пользователь {message.from_user.id} сделал IP lookup: {ip}')
        bot.send_message(message.chat.id, result)
    except:
        bot.send_message(message.chat.id, "Использование: /ip [ip адрес]")

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

@bot.message_handler(commands=['metadata'])
def metadata_command(message):
    user_waiting_photo[message.from_user.id] = True
    bot.send_message(message.chat.id, "Отправь фото, чтобы я проверил метаданные.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if not user_waiting_photo.get(user_id):
        return
    user_waiting_photo[user_id] = False

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = f"{file_info.file_unique_id}.jpg"
        with open(file_name, 'wb') as f:
            f.write(downloaded_file)

        metadata = extract_exif(file_name)
        os.remove(file_name)

        if metadata:
            bot.send_message(message.chat.id, "Метаданные изображения:\n\n" + metadata)
        else:
            bot.send_message(message.chat.id, "EXIF-метаданные отсутствуют.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при обработке изображения: {e}")

def extract_exif(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()

        if not exif_data:
            return None

        result = ""
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            result += f"{tag}: {value}\n"

        return result.strip()
    except Exception as e:
        return f"Ошибка при извлечении EXIF: {e}"

@bot.message_handler(func=lambda message: True)
def log_all(message):
    logging.info(f'Пользователь {message.from_user.id} написал сообщение: {message.text}')

bot.polling(none_stop=True, interval=0)
