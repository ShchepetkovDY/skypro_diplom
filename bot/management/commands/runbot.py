import logging

from telebot import TeleBot
from telebot.types import Message

from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from goals.models import Goal, GoalCategory, BoardParticipant

# =============== Enable logging  ==============================
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("start bot")

user_states = {'state': {}}
cat_id = []

logger.info(user_states)
logger.info(cat_id)

bot = TeleBot(settings.BOT_TOKEN, threaded=False)

allowed_commands = ['/goals', '/create', '/cancel']


@bot.message_handler(commands=['start', 'help', 'cancel'])
def handle_user_without_verification(msg: Message):
    """ Проверочный код. Обрабатывать пользователя без проверки """
    tg_user, _ = TgUser.objects.get_or_create(user_ud=msg.from_user.id,
                                              defaults={"chat_id": msg.chat.id, "username": msg.from_user.username})

    if tg_user.user:
        send_welcome(msg)

    else:
        bot.send_message(
            msg.chat.id,
            'Добро пожаловать!\n'
            'Для продолжения работы необходимо привязать\n'
            'Ваш аккаунт на сайте http://51.250.18.239/\n',
        )
        tg_user.set_verification_code()
        tg_user.save(update_fields=["verification_code"])
        bot.send_message(msg.chat.id, f"Верификационный  код: {tg_user.verification_code}")

    if 'user' in user_states['state']:
        del user_states['state']['user']
        del user_states['state']['chat_id']
        bot.send_message(tg_user.chat_id, 'Операция отменена')
        if 'category' in user_states['state']:
            del user_states['state']['category']

        if 'goal_title' in user_states['state']:
            del user_states['state']['goal_title']

        if 'description' in user_states['state']:
            del user_states['state']['description']

        if 'due_date' in user_states['state']:
            del user_states['state']['due_date']


def send_welcome(msg: Message):
    """ Отправка приветственного сообщения и помощи в командах """
    if msg.text == '/start':
        bot.send_message(msg.chat.id, f"Приветствую! {msg.chat.first_name}\n"
                                      'Бот может работать и обрабатывает следующие команды:\n'
                                      '/board -> выводит список досок задач\n'
                                      '/category -> выводит список категорий\n'
                                      '/goals -> выводит список целей\n'
                                      '/create -> позволяет создавать новые цели\n'
                                      '/cancel -> позволяет отменить создание цели (только на этапе создания)\n')

    elif ('user' not in user_states['state']) and (msg.text not in allowed_commands):
        bot.send_message(msg.chat.id, 'Неизвестная команда')


@bot.message_handler(chat_types=['private'])
def handle_message(msg: Message):
    """ Обработка команд и вывод полученных данных из БД в Телеграмм """
    tg_user, _ = TgUser.objects.get_or_create(user_ud=msg.from_user.id,
                                              defaults={"chat_id": msg.chat.id, "username": msg.from_user.username})

    if msg.text == '/board':
        boards = BoardParticipant.objects.filter(user=tg_user.user)
        if boards:
            [bot.send_message(msg.chat.id, f"Название карточек: {item.board}\n") for item in boards]
        else:
            bot.send_message(msg.chat.id, "Нет у вас Board")

    elif msg.text == '/category':
        resp_categories: list[str] = [
            f'{category.id} {category.title}'
            for category in GoalCategory.objects.filter(
                board__participants__user=tg_user.user_id, is_deleted=False)]
        if resp_categories:
            bot.send_message(msg.chat.id, "🏷 Ваши категории\n===================\n" + '\n'.join(resp_categories))
        else:
            bot.send_message(msg.chat.id, 'У Вас нет ни одной категории!')

    elif msg.text == '/goals':
        goals = Goal.objects.filter(user=tg_user.user)
        if goals.count() > 0:
            [bot.send_message(tg_user.chat_id,
                              f'Название: {goal.title},\n'
                              f'Категория: {goal.category},\n'
                              f'Описание: {goal.description},\n'
                              f'Статус: {goal.get_status_display()},\n'
                              f'Пользователь: {goal.user},\n'
                              f'Дедлайн {goal.due_date if goal.due_date else "Нет"} \n') for goal in goals]
        else:
            bot.send_message(msg.chat.id, "Список целей пуст.")

    # ===================== CREATE GOALS ===========================================
    elif msg.text == '/create':
        categories = GoalCategory.objects.filter(user=tg_user.user)
        if categories.count() > 0:
            cat_text = ''
            for cat in categories:
                cat_text += f'{cat.id}: {cat.title} \n'
                cat_id.append(cat.id)
            bot.send_message(chat_id=tg_user.chat_id,
                             text=f'Выберите номер категории для новой цели:\n========================\n{cat_text}'
                                  f'Или нажмите /cancel для отмены')

            if 'user' not in user_states['state']:
                user_states['state']['user'] = tg_user.user
                user_states['state']['chat_id'] = tg_user.chat_id

    elif (msg.text not in allowed_commands) and (user_states['state']['user']) \
            and ('category' not in user_states['state']):
        category = handle_save_category(msg, tg_user)
        if category:
            user_states['state']['category'] = category
            bot.send_message(tg_user.chat_id, f'Выбрана категория:\n {category}.\nВведите заголовок цели.')

    # =============== ВВОД ЗАГОЛОВКА И ЗАПРОС НА ОПИСАНИЕ =============
    elif (msg.text not in allowed_commands) and (user_states['state']['user']) \
            and (user_states['state']['category']) and ('goal_title' not in user_states['state']):
        user_states['state']['goal_title'] = msg.text
        bot.send_message(msg.chat.id, 'Введите описание')

    # =============== ВВОД ОПИСАНИЯ И ЗАПРОС НА ДЕДЛАЙН ===============
    elif (msg.text not in allowed_commands) and (user_states['state']['user']) \
            and (user_states['state']['category']) and ('description' not in user_states['state']):
        user_states['state']['description'] = msg.text
        bot.send_message(msg.chat.id, 'Введите дату дедлайна в формате ГГГГ-ММ-ДД(2022-01-01)')

    # ============== ВВОД ДЕДЛАЙНА И СОХРАНЕНИЯ В БД ==================
    elif (msg.text not in allowed_commands) and (user_states['state']['user']) \
            and (user_states['state']['category']) and ('due_date' not in user_states['state']):
        user_states['state']['due_date'] = msg.text

        goal = Goal.objects.create(title=user_states['state']['goal_title'],
                                   user=user_states['state']['user'],
                                   category=user_states['state']['category'],
                                   description=user_states['state']['description'],
                                   due_date=user_states['state']['due_date'])

        logger.info(goal)
        logger.info(cat_id)
        logger.info(user_states)

        bot.send_message(tg_user.chat_id, f'Цель: {goal.title} создана в БД')
        del user_states['state']['user']
        del user_states['state']['chat_id']
        del user_states['state']['category']
        del user_states['state']['goal_title']
        del user_states['state']['description']
        del user_states['state']['due_date']
        cat_id.clear()
        logger.info(user_states)
    # =============== END CREATE GOALS ==========================================================
    elif msg.text not in allowed_commands:
        bot.send_message(msg.chat.id, 'Неизвестная команда')


def handle_save_category(msg: Message, tg_user: TgUser):
    """ Обрабатыватывает категории для сохранения """
    category_id = int(msg.text)
    category_data = GoalCategory.objects.filter(user=tg_user.user).get(pk=category_id)
    return category_data


class Command(BaseCommand):
    help = "run bot"

    def handle(self, *args, **options):
        bot.polling()