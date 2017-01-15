import fileinput
import re
import os
from telepot.namedtuple import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton


class UsersHandle:
    """
    Manages user database
    """

    def __init__(self, path='users'):
        self.path = path  # file location
        self.data = {}  # users
        self.pending_update = {}  # temp dictionary for updates
        self.read_data_base()

    def update_user(self, from_id, delete=False, user_delete=False, *args, **kwargs):
        """
        If user exist, update his setting (or delete), else create new user.
        Call's self.save_on_disk()

        :type from_id: int
        :param from_id: user or chat id (they are equal)
        :type delete: bool
        :param delete: delete field from file
        :type user_delete: bool
        :param user_delete: delete user from file
        :type args: list
        :param args: use only with delete=True, list of strings of parameters to delete
        :type kwargs: dict
        :param kwargs: dict of {preference<class 'str'>:value<class 'str'>}
        :return: None
        """
        if not self.user_exist(from_id):  # add user
            self.pending_update[from_id], self.data[from_id] = {}, {}
            for key in kwargs.keys():
                self.pending_update[from_id][key], self.data[from_id][key] = kwargs[key], kwargs[key]
            self.save_on_disk('a')

        elif user_delete:
            self.pending_update[from_id] = {}
            del self.data[from_id]
            self.save_on_disk(user_delete=True)

        elif delete:  # delete field from file
            self.pending_update[from_id] = {}
            for obj in args:
                self.pending_update[from_id][obj] = None
                del self.data[from_id][obj]
            self.save_on_disk(delete=True)

        else:  # change user setting
            self.pending_update[from_id] = {}
            for key in kwargs.keys():
                self.pending_update[from_id][key], self.data[from_id][key] = kwargs[key], kwargs[key]
            self.save_on_disk()

        self.pending_update.clear()

    def save_on_disk(self, mode='w', delete=False, user_delete=False):
        """
        Save user database on disk

        :type mode: str
        :param mode: if 'w', whole file is rewrited, useful for changes; elif 'a', append line to file
        :type delete: bool
        :param delete: delete field from file
        :type user_delete: bool
        :param user_delete: delete user from file
        :return: None
        """
        no_skip, new_line = True, True

        count = 0

        if mode == 'w':  # replace
            with fileinput.FileInput(self.path, True, '.tmp') as file:
                for line in file:
                    if len(line) < 2:
                        continue

                    if '\n' in line:
                        line = line[:len(line) - 1]

                    for key, data in self.pending_update.items():
                        if str(key) not in line:  # search for user
                            continue

                        if user_delete:  # skip, don't write to file
                            no_skip = False
                            continue


                        for key2, data2 in data.items():
                            temp = re.search(r'\b{}\S*'.format(key2), line)  # try to build full string to replace later
                            if temp is None:  # new property
                                line += ' {}={}'.format(key2, data2)
                                continue

                            else:
                                rep = temp.group()  # build full string to replace
                                if delete:  # delete full string and 1 space before
                                    rep = ' ' + rep
                                    line = line.replace(rep, '')
                                    continue
                                if rep == '{}={}'.format(key2, data2):  # new setting has same value
                                    continue
                            line = line.replace(rep, '{}={}'.format(key2, data2))  # replace property
                            # line = line[:len(line)]
                            # new_line = False

                    if no_skip:
                        '''if new_line:
                            print(line)
                            #new_line = False
                            continue'''

                        print(line)  # print line to file
                        count += 1
                    no_skip = new_line = True

        elif mode == 'a':  # append
            with open(self.path, mode=mode, encoding='utf-8') as file:
                pattern = 'id={}'
                '''if os.stat(self.path).st_size == 0:
                    pattern = 'id={}'''
                for user_id in self.pending_update.keys():
                    file.write(pattern.format(user_id))
                    for obj in self.pending_update[user_id].keys():
                        file.write(' {}={}'.format(obj, self.pending_update[user_id][obj]))

        print(count)

    def read_data_base(self):
        """
        Read data from self.path file and store in self.data

        Why file? Because I can't mysql. For now.

        :return: None
       """
        with open(self.path, encoding='utf-8') as file:
            for line in file:  # 'id=1313 pass=sdfe setting=None'
                if len(line) > 2:  # can be len('\n') == 1 #check
                    line = line.rstrip().split()  # ['id=1313', 'pass=sdfe', 'setting=None']
                    line = [item.split('=') for item in
                            line]  # [['id', '1313'], ['pass', 'sdfe'], ['setting', 'None']]
                    self.data[int(line[0][1])] = dict(line[1:])
                    '''
                    self.data == {242424:{  'fac':'ИУ',
                                            'kaf':'3'
                                            #and so on...
                                            }
                                 }
                    '''

                    '''
                    some bad code example
                    actually equal to self.data[int(line[0][1])] = dict(line[1:])
                    temp = []

                    for item in line:  # item == ['id', '1313']
                        for obj in item:  # obj == 'id' and so on...
                            temp.append(obj)

                    it = iter(temp)  # temp == ['id', '1313', 'pass', 'sdfe', 'setting', 'None']
                    it.__next__()  # 'id' <class 'str'>
                    id = int(it.__next__())  # id <class 'int'>
                    self.data[id] = dict(zip(it, it))  # self.data[id] = dict of all the rest
                    '''

    def user_exist(self, from_id):
        """
        Check if id in self.data

        :type from_id: int
        :param from_id: user or chat id (they are equal)
        :return: Bool
        """
        if from_id in self.data:
            return True
        else:
            return False

    def get(self, from_id, field):
        """
        Get user's setting property

        :type from_id: int
        :param from_id: user or chat id (they are equal)
        :type field: str
        :param field: setting key
        :return: str or None
        """
        if not self.user_exist(from_id):
            return None
        elif field in self.data[from_id]:
            return self.data[from_id][field]
        return None

    def registered(self, from_id):
        """
        Check if registration is complete

        :type from_id: int
        :param from_id: user or chat id (they are equal)
        :return: Boll
        """
        if from_id in self.data:
            needed = set(['faculty', 'kafedra', 'group'])
            if needed.issubset(set(self.data[from_id])):
                for obj in needed:
                    if len(self.data[from_id][obj]) == 0:
                        return False
                return True
        return False


def build_inline_keyboard(data, type='', back_button='', rows=2):
    """
    Builds buttons for keyboards, callback_data=data[index] + ' ' + type

    :type data: list
    :param data: list of strings buttons text
    :type type: str
    :param type: callback type
    :type rows: int
    :param rows: number of button rows
    :return: InlineKeyboardMarkup object
    """
    buttons = [[]]
    if len(back_button) > 0:
        buttons[-1].append(InlineKeyboardButton(text='<', callback_data='goback:' + back_button + ' start_routine'))
        buttons.append([])
    for obj in data:
        if len(buttons[-1]) < rows:
            # пробел в callback_data может глючить
            buttons[-1].append(InlineKeyboardButton(text=obj, callback_data=obj + ' ' + type))
        else:
            buttons.append([InlineKeyboardButton(text=obj, callback_data=obj + ' ' + type)])  # new list
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_keyboard(data, rows=2, resize_keyboard=False, one_time_keyboard=False, selective=False):
    """
    Builds buttons for keyboards, callback_data=data[index] + ' ' + type

    :type data: list
    :param data: list of strings buttons text
    :type rows: int
    :param rows: number of button rows
    :type resize_keyboard: bool
    :param resize_keyboard: read telegram api on Available types/ReplyKeyboardMarkup
    :type one_time_keyboard: bool
    :param
    :type selective: bool
    :param
    :return: ReplyKeyboardMarkup object
    """
    buttons = [[]]
    for obj in data:
        if len(buttons[-1]) < rows:
            # пробел в callback_data может глючить
            buttons[-1].append(KeyboardButton(text=obj))
        else:
            buttons.append([KeyboardButton(text=obj)])  # new list
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=resize_keyboard, one_time_keyboard=one_time_keyboard,
                               selective=selective)
