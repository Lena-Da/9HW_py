import logging
from tabnanny import check
from tokenize import Token
from config import TOKEN
from random import randint
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


BUTTON, BOT, HUMAN = range(3)



def start(update, _):
    reply_keyboard = [['Старт', 'Выход']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        'Это игра в конфеты. '
        'Играть вы будете с ботом, нужно брать от 1 до 3 конфет. '
        'Проиграет тот, кто заберет последние. '
        'Команда /cancel, чтобы выйти из игры.\n\n',
        reply_markup=markup_key,)
    return BUTTON

def button(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s нажимает %s", user.first_name, update.message.text)
    choice = update.message.text
    if choice == 'Старт':
        logger.info("Первый ход человека")
        update.message.reply_text('Вы начинаете игру. Всего 100 конфет \n' "Введите число от 1 - 3: ",reply_markup=ReplyKeyboardRemove())
        return HUMAN
    if choice == 'Выход':
        return skip_game(update, _)    


def human(update, _):
    count=100
    user = update.message.from_user
    num = update.message.text("Введите число от 1 - 3: ")
    logger.info("Пользователь %s забирает %s", user.first_name, update.message.text)
    num_int=int(num)
    count=count-num_int
    update.message.reply_text(f'Осталось {count} конфет')
    if count == 0:
            update.message.reply_text(f'GAME OVER\nВы выиграли!')
            return ConversationHandler.END
    return BOT

def bot(update, _):
    num = randint(1,3)
    update.message.reply_text(f'Бот вводит {num}')
    count=count-num
    update.message.reply_text(f'Осталось {count} конфет')
    if count == 0:
            update.message.reply_text(f'GAME OVER\nВыиграл бот!')
            return ConversationHandler.END

    return HUMAN


def skip_game(update, _):
    user = update.message.from_user
    logger.info("Пользователь %s отменил разговор.", user.first_name)
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться'
        ' Будет скучно - пиши.', 
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


if __name__ == '__main__':
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BUTTON: [MessageHandler(Filters.text, button,CommandHandler('cancel', skip_game))],
            HUMAN: [MessageHandler(Filters.text, human), CommandHandler('cancel', skip_game)],
            BOT: [MessageHandler(Filters.text, bot), CommandHandler('cancel', skip_game)],
        },
        fallbacks=[CommandHandler('cancel', skip_game)],
    )


dispatcher.add_handler(conv_handler)


updater.start_polling()
updater.idle()



