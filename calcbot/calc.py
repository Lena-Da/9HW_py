import logging
from tokenize import Token
from config import TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



BUTTON, FIRST_NUM, SECOND_NUM, CALCULATION = range(4)



def start(update, _):
    reply_keyboard = [['Старт', 'Выход']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        'Этот калькулятор работает с рациональными числами. \n'
        'Если нужно что-то посчитать, выбирайте Старт. \n',
        reply_markup=markup_key,)
    return BUTTON

def button(update, context):
    user = update.message.from_user
    logger.info("Пользователь %s нажимает %s", user.first_name, update.message.text)
    choice = update.message.text
    if choice == 'Старт':
        update.message.reply_text('Введите первое рациональное число с точкой',reply_markup=ReplyKeyboardRemove())
        return FIRST_NUM
    if choice == 'Выход':
        return cancel(update, context)


def first_num(update, context):
    user = update.message.from_user
    logger.info("Пользователь %s вводит число %s", user.first_name, update.message.text)
    rational = update.message.text
    if rational==str(float(rational)):
        rational = float(rational)
        context.user_data['first_num'] = rational
        update.message.reply_text('Введите второе рациональное число с точкой''Для выхода /cancel \n')
        return SECOND_NUM
    else:
        update.message.reply_text('Неверный ввод')


def second_num(update, context):
    user = update.message.from_user
    logger.info("Пользователь %s вводит число %s", user.first_name, update.message.text)
    rational = update.message.text
    if rational == str(float(rational)):
        rational = float(rational)
        context.user_data['second_num'] = rational
        update.message.reply_text('Доступные операции: +, -, *, / \n''Выберите и введите \n''Для выхода /cancel \n')
        return CALCULATION
    else:
        update.message.reply_text('Неверный ввод')


def calculation(update, context):
    user = update.message.from_user
    logger.info("Пользователь %s выбирает операцию %s", user.first_name, update.message.text)
    first = context.user_data.get('first_num')
    second = context.user_data.get('second_num')
    operation = update.message.text
    if operation == '+':
        result = first + second
    if operation == '-':
        result = first - second
    if operation == '*':
        result = first * second
    if operation == '/':
        try:
            result = first / second
        except:
            update.message.reply_text('Делить на 0 нельзя')
    update.message.reply_text(
        f'Результат: {first} {operation} {second} = {result} \n' 
        'Запустить еще раз - /start')
    return ConversationHandler.END




def cancel(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
        'Запустить - /start', 
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    conversation_handler = ConversationHandler(  
        entry_points=[CommandHandler('start', start)],
        states={
            BUTTON: [MessageHandler(Filters.text, button,CommandHandler('cancel', cancel))],
            FIRST_NUM: [MessageHandler(Filters.text, first_num),CommandHandler('cancel', cancel)],
            SECOND_NUM: [MessageHandler(Filters.text, second_num),CommandHandler('cancel', cancel)],
            CALCULATION: [MessageHandler(Filters.text, calculation),CommandHandler('cancel', cancel)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


    dispatcher.add_handler(conversation_handler)


    print('server started')
    updater.start_polling()
    updater.idle()
