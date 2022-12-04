import os, telebot, datetime, uuid, emoji
from telebot import types
from db import *

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
commands = [types.BotCommand(command="support", description="Оставить обращение в техподдержку"), types.BotCommand(command="getunreads", description="Ответить на сообщение клиента")]
bot.set_my_commands(commands)

isRunning = False

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    global isRunning
    if not isRunning:
        bot.send_message(message.chat.id, emoji.emojize('Привет! :waving_hand_light_skin_tone: Это чат технической поддержки. Открой меню, чтобы увидеть команды'))
        isRunning = True

@bot.message_handler(commands=['support'])
def support_handler(message=""):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(emoji.emojize("Отмена :cross_mark:")))
    msg = bot.send_message(chat_id, emoji.emojize('Здесь ты можешь оставить свое обращение :pencil:'), reply_markup=markup)
    bot.register_next_step_handler(msg, addToDB)
def addToDB(message):
    global isRunning
    chat_id = message.chat.id
    text = message.text 
    if (text == emoji.emojize("Отмена :cross_mark:")):
        bot.send_message(chat_id, 'Вы отменили действие',reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
        return
    uuid1 = uuid.uuid1()
    now = datetime.datetime.now()
    try:
        sql_add(connect_db(), (chat_id, now, message.text, 0, str(uuid1)))
        bot.send_message(chat_id, 'Спасибо за Ваше обращение. Наш специалист скоро ответит на Ваш вопрос!', reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
    except:
        bot.send_message(chat_id, 'Что то пошло не так, попробуй снова',reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
        bot.register_next_step_handler(support_handler)
    isRunning = False    


@bot.message_handler(commands=['getunreads'])
def getUnreads_handler(message=""):
    chat_id = message.chat.id
    try:
        questions = sql_out()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btnList = []
        btnList.append(types.KeyboardButton(emoji.emojize("Отмена :cross_mark:")))
        for question in questions:
            btnList.append(types.KeyboardButton(question[1]))    
        markup.add(*btnList)    
        msg = bot.send_message(chat_id, text="Выбери ID непрочитанного вопроса, чтобы ответить", reply_markup=markup)
        bot.register_next_step_handler(msg, searchUnreadQuestion)
    except:
        bot.send_message(chat_id, 'Что то пошло не так, попробуй снова')
        bot.register_next_step_handler(getUnreads_handler)    

def searchUnreadQuestion(message):
    chat_id = message.chat.id
    text = message.text
    if (text == emoji.emojize("Отмена :cross_mark:")):
        bot.send_message(chat_id, 'Вы отменили действие',reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
        return
    question = sql_search(text)
    bot.send_message(chat_id, text=f"{question[0][0]}: {question[0][1]}. {question[0][2]}", reply_markup=types.ReplyKeyboardRemove(), parse_mode='Markdown')
    msg = bot.send_message(chat_id, emoji.emojize("Напишите здесь ответ для клиента и он будет отправлен в его чат :pencil:"))
    bot.register_next_step_handler(msg, answerTheQuestion, question[0][0], question[0][3])

def answerTheQuestion(message, client_id, question_id):
    global isRunning 
    text = message.text
    bot.send_message(client_id, text)
    sql_setRead(question_id)
    isRunning = False


bot.polling()


    