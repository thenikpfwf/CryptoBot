import telebot
from pycoingecko import CoinGeckoAPI
from telebot import types
from py_currency_converter import convert

bot = telebot.TeleBot("bot's api")  # замените на свой токен
cg = CoinGeckoAPI

# Начальное приветствие
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Здравствуйте! Выберите действие", reply_markup=main_menu())

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Посмотреть курс крипты'),
        types.KeyboardButton('Посмотреть курс фиата'),
        types.KeyboardButton('Конвертация')
    )
    return markup

# Курс криптовалюты
@bot.message_handler(func=lambda message: message.text == 'Посмотреть курс крипты')
def show_crypto_menu(message):
    bot.send_message(message.chat.id, 'Курс токенов', reply_markup=currency_menu())

# Курса фиата
@bot.message_handler(func=lambda message: message.text == 'Посмотреть курс фиата')
def fiat(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('USD'), types.KeyboardButton('RUB'), types.KeyboardButton('Назад'))
    q = bot.send_message(message.chat.id, 'Курс фиата', reply_markup=markup)
    bot.register_next_step_handler(q, fiat_step2)

@bot.message_handler(func=lambda message: message.text == 'Назад')
def go_back(message):
    bot.send_message(message.chat.id, "Вы вернулись в главное меню", reply_markup=main_menu())

# Конвертация
@bot.message_handler(func=lambda message: message.text == 'Конвертация')
def convert_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Bitcoin'),
        types.KeyboardButton('Ethereum'),
        types.KeyboardButton('Litecoin'),
        types.KeyboardButton('Solana'),
        types.KeyboardButton('TON'),
        types.KeyboardButton('Назад')
    )
    msg = bot.send_message(message.chat.id, 'Выберите криптовалюту', reply_markup=markup)
    bot.register_next_step_handler(msg, convert_amount)

# Обработка выбора криптовалюты для конвертации
def convert_amount(message):
    currency_dict = {
        'Bitcoin': 'bitcoin',
        'Ethereum': 'ethereum',
        'Litecoin': 'litecoin',
        'Solana': 'solana',
        'TON': 'the-open-network'
    }

    if message.text in currency_dict:
        msg = bot.send_message(message.chat.id, f'Сколько вы хотите конвертировать {message.text}?')
        bot.register_next_step_handler(msg, lambda msg: calculate_conversion(msg, currency_dict[message.text]))

# Расчет конверсии
def calculate_conversion(message, crypto_id):
    try:
        amount = int(message.text)
        price = cg.get_price(ids=crypto_id, vs_currencies='usd')
        bot.send_message(message.chat.id, f"{amount} = {amount * price[crypto_id]['usd']} $")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")

# Функции для отображения курсов фиата
@bot.message_handler(func=lambda message: message.text == 'USD')
def fiat_step2(message):
    price = convert(base='USD', amount=1, to=['RUB', 'EUR', 'UAH', 'KZT'])
    bot.send_message(message.chat.id,
                     f'1 USD = {price["RUB"]} ₽\n'
                     f'1 USD = {price["EUR"]} EUR\n'
                     f'1 USD = {price["UAH"]} UAH\n'
                     f'1 USD = {price["KZT"]} KZT')

@bot.message_handler(func=lambda message: message.text == 'RUB')
def fiat_rub(message):
    price = convert(base='RUB', amount=1, to=['USD', 'EUR', 'UAH', 'KZT'])
    bot.send_message(message.chat.id,
                     f'1 RUB = {price["USD"]} RUB\n'
                     f'1 RUB = {price["EUR"]} EUR\n'
                     f'1 RUB = {price["UAH"]} UAH\n'
                     f'1 RUB = {price["KZT"]} KZT')

# Меню выбора валюты
def currency_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Курс к USD'), types.KeyboardButton('Курс к RUB'), types.KeyboardButton('Назад'))
    return markup

bot.polling()