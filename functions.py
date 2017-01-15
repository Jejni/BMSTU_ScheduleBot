from telepot.namedtuple import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
import pickle
import lxml.html as html
import urllib.request
from selenium import webdriver
import re
import pprint


class UsersHandle:
    """
    Manages user database
    """

    def __init__(self, path='users.bin'):
        self.path = path  # file location
        self.data = {}  # users
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
            self.data[from_id] = {}
            for key in kwargs.keys():
                self.data[from_id][key] = kwargs[key]
            self.save_on_disk()

        elif user_delete:
            del self.data[from_id]
            self.save_on_disk()

        elif delete:  # delete field from file
            for obj in args:
                del self.data[from_id][obj]
            self.save_on_disk()

        else:  # change user setting
            for key in kwargs.keys():
                self.data[from_id][key] = kwargs[key]
            self.save_on_disk()

    def save_on_disk(self):
        """
        Save user database on disk

        :return: None
        """
        with open(self.path, 'wb') as file:
            pickle.dump(self.data, file)

    def read_data_base(self):
        """
        Read data from self.path file and store in self.data

        Why file? Because I can't mysql. For now.

        :return: None
       """
        try:
            with open(self.path, 'rb') as file:
                self.data = pickle.load(file)
        except (OSError, IOError):
            print('users_database not found')

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