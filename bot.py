import telebot # библиотека telebot
from config import token # импорт токена
import re # библиотека для работы с регулярными выражениями

bot = telebot.TeleBot(token) 

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для управления чатом.")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.reply_to_message: #проверка на то, что эта команда была вызвана в ответ на сообщение 
        chat_id = message.chat.id # сохранение id чата
        # сохранение id и статуса пользователя, отправившего сообщение
        user_id = message.reply_to_message.from_user.id
        user_status = bot.get_chat_member(chat_id, user_id).status 
        # проверка пользователя
        if user_status == 'administrator' or user_status == 'creator':
            bot.reply_to(message, "Невозможно забанить администратора.")
        else:
            bot.ban_chat_member(chat_id, user_id) # пользователь с user_id будет забанен в чате с chat_id
            bot.reply_to(message, f"Пользователь @{message.reply_to_message.from_user.username} был забанен.")
    else:
        bot.reply_to(message, "Эта команда должна быть использована в ответ на сообщение пользователя, которого вы хотите забанить.")

# Хэндлер для автоматического бана за ссылки
@bot.message_handler(func=lambda message: True)
def check_for_links(message):
    # Проверяем, не является ли сообщение командой (чтобы не банить за /start и /ban)
    if message.text and not message.text.startswith('/'):
        # Проверяем наличие ссылок в тексте
        if 'https://' in message.text or 'http://' in message.text or 'www.' in message.text:
            chat_id = message.chat.id
            user_id = message.from_user.id
            username = message.from_user.username
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            
            try:
                # Получаем статус пользователя
                user_status = bot.get_chat_member(chat_id, user_id).status
                
                # Проверяем, не является ли пользователь администратором
                if user_status == 'administrator' or user_status == 'creator':
                    bot.reply_to(message, "Администратор отправил ссылку, но не был забанен.")
                else:
                    # Сохраняем информацию о пользователе перед баном
                    user_info = (f"Забанен пользователь:\n"
                               f"ID: {user_id}\n"
                               f"Username: @{username}\n"
                               f"Имя: {first_name} {last_name if last_name else ''}\n"
                               f"Сообщение: {message.text}")
                    
                    # Баним пользователя
                    bot.ban_chat_member(chat_id, user_id)
                    
                    # Отправляем уведомление в чат
                    bot.send_message(chat_id, f"Пользователь @{username} был забанен за отправку ссылки.")
                    
                    # Выводим информацию в консоль (для админа)
                    print(user_info)
                    
            except Exception as e:
                print(f"Ошибка при бане пользователя: {e}")
                bot.reply_to(message, "Произошла ошибка при попытке забанить пользователя.")

# Новый хэндлер для приветствия новых участников
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        # Отправляем приветственное сообщение
        welcome_text = (f"Добро пожаловать, {new_member.first_name}!\n"
                       f"Рады видеть тебя в нашем чате! 👋\n"
                       f"Ознакомься с правилами чата, чтобы избежать неприятных ситуаций.")
        
        bot.send_message(message.chat.id, welcome_text)
        
        # Пытаемся одобрить запрос на вступление (если требуется)
        try:
            bot.approve_chat_join_request(message.chat.id, new_member.id)
            print(f"Запрос на вступление одобрен для пользователя {new_member.first_name} (ID: {new_member.id})")
        except Exception as e:
            # Если функция не поддерживается или запрос не требуется, просто игнорируем
            print(f"Не удалось одобрить запрос: {e}")

bot.infinity_polling(none_stop=True)