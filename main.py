import telepot.aio
from telepot.namedtuple import ReplyKeyboardHide, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton

import functions
from functions import build_inline_keyboard, build_keyboard
import asyncio
import time

TOKEN = ''


def build_text_schedule(msg):
    from_id = msg['from']['id']
    ff = ''
    for day in sc.groups(users, from_id)[users.get(from_id, 'group')]['чс']:
        ff += '\n' + day + ':\n'
        for time in sc.groups(users, from_id)[users.get(from_id, 'group')]['чс'][day]:
            ff += time + ': ' + \
                  sc.groups(users, from_id)[users.get(from_id, 'group')]['чс'][day][
                      time] + '\n'
    return ff


def sort_key(str):
    return int(str.split(':')[0])


def days_sort_key(day):
    temp = {'понедельник': 0,
            'вторник': 1,
            'среда': 2,
            'четверг': 3,
            'пятница': 4,
            'суббота': 5,
            'воскресенье': 6
            }
    return temp[day]


def build_inline_schedule(msg, day):
    from_id = msg['from']['id']
    buttons = [[]]
    data = sc.days(users, from_id)
    mdata = list(data)
    mdata.sort(key=days_sort_key)
    mdata = mdata[:3]
    for obj in mdata:
        buttons[-1].append(
            InlineKeyboardButton(text=obj if not obj == day else '>{}<'.format(obj), callback_data=obj + ' schedule'))

    data = sc.xxx(users, from_id, day)
    mdata = list(data)
    mdata.sort(key=sort_key)

    for obj in mdata:
        if data[obj]['чс'] is None or data[obj]['зн'] is None:
            continue
        if data[obj]['чс'] == data[obj]['зн']:
            buttons.append([InlineKeyboardButton(text=obj + ' (чс, зн)', callback_data='None callback')])
            buttons.append([InlineKeyboardButton(text=data[obj]['чс'], callback_data='None callback')])
        else:
            buttons.append([InlineKeyboardButton(text=obj, callback_data='None callback')])
            for item in data[obj]:
                text = data[obj][item]
                if text == '-------- ( )':
                    continue
                buttons.append([InlineKeyboardButton(text=item + ' ' + text, callback_data='None callback')])
    buttons.append([])

    data = sc.days(users, from_id)
    mdata = list(data)
    mdata.sort(key=days_sort_key)
    mdata = mdata[3:]
    for obj in mdata:
        buttons[-1].append(
            InlineKeyboardButton(text=obj if not obj == day else '>{}<'.format(obj),
                                 callback_data=obj + ' schedule'))
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def show(msg, type='message'):
    # await bot.sendMessage(msg['from']['id'], build_text_schedule(msg))
    day = 'понедельник'
    if type == 'schedule':
        day = msg['data'].split()[0]
        message = telepot.message_identifier(msg['message'])
        await bot.editMessageText(message, 'Расписание: ', reply_markup=build_inline_schedule(msg, day))
        return

    await bot.sendMessage(msg['from']['id'], 'Расписание: ', reply_markup=build_inline_schedule(msg, day))


async def start_routine(msg, type='iniciate'):
    from_id = msg['from']['id']
    if users.registered(from_id):
        users.update_user(from_id, last_message_from=':/start')
        await bot.sendMessage(from_id, 'С возвращением!', reply_markup=ReplyKeyboardHide())
        return

    if type == 'iniciate':
        send_query = [
            'Привет, {}!'.format(msg['from']['first_name']),
            ' Рад тебя видеть :=)',
            'Я помогу тебе не потеряться в твоих студенческих буднях))',
        ]
        for message in send_query:
            await bot.sendMessage(from_id, text=message, reply_markup=ReplyKeyboardHide())
            # time.sleep(1.5)
        text = 'Давай знакомиться :3'
        message = await bot.sendMessage(from_id, text=text)
        message = telepot.message_identifier(message)
        text = 'Выбери факультет: '
        await bot.editMessageText(message, text,
                                  reply_markup=build_inline_keyboard(sc.faculties(), 'start_routine'))


    elif type == 'start_routine':
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        message = telepot.message_identifier(msg['message'])

        if 'goback' in query_data:
            query_data = query_data.split()[0].split(':')[1]
        else:
            query_data = query_data[::-1].split(maxsplit=1)[1][::-1]
            print(query_data)

        if query_data == 'begin_again':
            await bot.editMessageText(message, 'Выбери факультет: ',
                                      reply_markup=build_inline_keyboard(sc.faculties(), 'start_routine'))

        elif query_data in sc.faculties():
            users.update_user(from_id, faculty=query_data, last_message_to='start_routine:faculties')
            await bot.editMessageText(message, 'Выбери кафедру: ',
                                      reply_markup=build_inline_keyboard(sc.kafs(users, from_id), 'start_routine',
                                                                         'begin_again'))

        elif query_data in sc.kafs(users, from_id):
            users.update_user(from_id, kafedra=query_data, last_message_to='start_routine:kafs')
            await bot.editMessageText(message, 'Выбери группу: ',
                                      reply_markup=build_inline_keyboard(sc.groups(users, from_id), 'start_routine',
                                                                         users.get(from_id, 'faculty')))

        elif query_data in sc.groups(users, from_id):
            users.update_user(from_id, group=query_data, last_message_to='start_routine:complete')
            '''
            start_routine:groups cause bug, because there is second field called groups
            need to fix regex
            '''
            await bot.editMessageText(message, '''Поддерживаемые команды:\n
/help - описание\n
/settings - настройки\n
/show (show) - показать расписание
''')
            await show(msg)


async def settings(msg):
    from_id = msg['from']['id']
    await bot.sendMessage(from_id, 'Настройки:',
                          reply_markup=build_keyboard(['Удалить профиль', 'Сменить группу'], one_time_keyboard=True))


async def change_group(msg):
    from_id = msg['from']['id']
    users.update_user(from_id, True, False, 'group')
    await bot.sendMessage(from_id, 'Выбери группу: ',
                          reply_markup=build_inline_keyboard(sc.groups(users, from_id), 'start_routine',
                                                             users.get(from_id, 'faculty')))


async def delete(msg):
    from_id = msg['from']['id']
    users.update_user(from_id, user_delete=True)
    await bot.sendMessage(from_id, 'So sorry to see you go, please, comeback..')


commands = {'/start': start_routine,
            # '/help':
            '/settings': settings,
            'Сменить группу': change_group,
            'Удалить профиль': delete,
            '/show': show,
            'show': show
            }

callback_commands = {
    'start_routine': start_routine,
    'schedule': show
}


async def on_chat_message(msg):
    from_id = msg['from']['id']
    if users.registered(from_id):
        if msg['text'] in commands:
            await commands[msg['text']](msg)
        else:
            await bot.sendMessage(from_id, 'Прости, такой команды нет :(')
    else:
        await start_routine(msg)


async def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print(query_data)
    query_data = query_data[::-1].split(maxsplit=1)[0][::-1]
    print(query_data)
    if query_data in callback_commands:
        await callback_commands[query_data](msg, query_data)


'''bot_delegator = telepot.aio.DelegatorBot(TOKEN, [(per_chat_id(), create_open(Handle, timeout=3600))])
bot = telepot.Bot(TOKEN)
loop = asyncio.get_event_loop()
loop.create_task(bot_delegator.message_loop())
loop.run_forever()'''

users = functions.UsersHandle()
sc = functions.schedule()

bot = telepot.aio.Bot(TOKEN)
loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop({'chat': on_chat_message,
                                   # 'edited_chat': on_edited_chat_message,
                                   'callback_query': on_callback_query
                                   # 'inline_query': on_inline_query,
                                   # 'chosen_inline_result': on_chosen_inline_result}))
                                   }))
print('Listening ...')
loop.run_forever()
