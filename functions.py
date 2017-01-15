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


class schedule:
    def __init__(self, path='schedule.bin'):
        self.path = path  # file location
        self.root_url = 'http://www.bmstu.ru/mstu/undergraduate/schedule'
        self.urls = []

        self.data = {}  # users
        self.read_data_base()

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
            print('schedule_database not found')

    def save_on_disk(self):
        """
        Save user database on disk

        :return: None
        """
        with open(self.path, 'wb') as file:
            pickle.dump(self.data, file)

    def build_links(self):
        page = urllib.request.urlopen(self.root_url).read()
        page = html.fromstring(page)
        page = page.findall(".//*[@class='row vt-listgroup']/div/table/tbody/tr/td/a")
        for element in page:
            self.urls.append(self.root_url + element.attrib['href'])

    def add_to_dict(self, *args):
        if len(args) == 3:
            faculty, kaf, group = args[0], args[1], args[2]
            if faculty in self.data:
                if kaf in self.data[faculty]:
                    self.data[faculty][kaf][group] = {}
                else:
                    self.data[faculty][kaf] = {group: {}}
            else:
                self.data[faculty] = {kaf: {group: {}}}
        if len(args) == 7:
            faculty, kaf, group, day, time, type, what = args[0], args[1], args[2], args[3], args[4], args[5], args[6]
            if day in self.data[faculty][kaf][group]:
                if time in self.data[faculty][kaf][group][day]:
                    self.data[faculty][kaf][group][day][time][type] = what
                else:
                    self.data[faculty][kaf][group][day][time] = {type: what}
            else:
                self.data[faculty][kaf][group][day] = {time: {type: what}}

    def clean_me_all_prop(self, all_prop):
        for key in all_prop.keys():
            cell = all_prop[key]
            if int(cell.attrib['rowspan']) in [0, 1]:
                del all_prop[key]
                self.clean_me_all_prop(all_prop)
                return

    def build_full_row(self, row, all_prop):
        cell_count = 0
        text_append = 0
        text_itself = ''
        for cell in row:

            if cell_count in all_prop:
                cell.text = all_prop[cell_count].text
                mmcell = all_prop[cell_count]
                temp = int(mmcell.attrib['rowspan'])
                temp -= 1
                mmcell.attrib['rowspan'] = str(temp)
                if 'colspan' in all_prop[cell_count].attrib and int(all_prop[cell_count].attrib['colspan']) > 1:
                    # print('Test_scan_prop_colspan: ', cell.text)
                    text_append = int(all_prop[cell_count].attrib['colspan'])
                    text_itself = all_prop[cell_count].text

            if text_append > 0:
                cell.text = text_itself
                text_append -= 1
            elif text_append == 0:
                text_append = -1
                text_itself = ''

            cell_count += 1

        self.clean_me_all_prop(all_prop)

        return row

    def scan_prop(self, row, all_prop, new_prop, days):
        cell_count = 0

        text_append = 0
        text_itself = ''

        for cell in row:  # use intersection
            if text_append > 1:
                cell.text = text_itself
                text_append -= 1
            elif text_append == 1:
                text_append = 0
                text_itself = ''

            if cell_count == 1 and 'style' not in cell.attrib:
                cell.text = days.pop(0)
            if 'rowspan' in cell.attrib and int(cell.attrib['rowspan']) > 1:
                if 'colspan' in cell.attrib and int(cell.attrib['colspan']) > 1:
                    new_prop[cell_count] = cell
                    # print('Test_scan_prop_colspan: ', cell.text)
                    text_append = int(cell.attrib['colspan'])
                    text_itself = cell.text
                new_prop[cell_count] = cell
                # print('Test_scan_prop_rowspan: ', cell.text)
            elif 'colspan' in cell.attrib and int(cell.attrib['colspan']) > 1:
                # print('Test_scan_prop_colspan: ', cell.text)
                text_append = int(cell.attrib['colspan'])
                text_itself = cell.text

            cell_count += 1

        row = self.build_full_row(row, all_prop)

        all_prop.update(new_prop)
        new_prop.clear()

        # print_row(row)

        return row

    def build_schedule(self):
        self.build_links()

        driver = webdriver.PhantomJS()

        print(len(self.urls))

        for url in self.urls:
            print(self.urls.index(url))

            driver.get(url)
            page = html.fromstring(driver.page_source)

            table = page.find(".//*[@class='wtHolder ht_master']/div/div/table/tbody")
            days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
            firstrow = True
            save_to_later = []
            all_prop = {}
            new_prop = {}
            row_count = 0

            for row in table:
                row_count += 1
                if row_count > 999:
                    continue

                if firstrow:  # тут названия групп
                    skip = 4
                    for cell in row:
                        if skip != 0:  # первые 4 клетки не нужны, прокручиваем до групп
                            skip -= 1
                            continue
                        group = cell.text
                        group = group.split('-')
                        group[0] = re.split('(\d+)', group[0])
                        self.add_to_dict(group[0][0], group[0][1], group[1])
                        save_to_later.append(group)
                    firstrow = False
                    continue

                row = self.scan_prop(row, all_prop, new_prop, days)
                cell_count = -2

                day = ''
                time = ''
                type = ''
                what = ''

                # print('Test_bigfor_row_len: ', len(row))

                for cell in row:
                    cell_count += 1
                    if cell_count == 0:
                        day = cell.text
                    elif cell_count == 1:
                        time = cell.text
                    elif cell_count == 2:
                        type = cell.text
                    elif cell_count > 2:
                        # print('Test_bigfor_cell_count: ', cell_count)
                        faculty = save_to_later[cell_count - 3][0][0]
                        kaf = save_to_later[cell_count - 3][0][1]
                        group = save_to_later[cell_count - 3][1]
                        self.add_to_dict(faculty, kaf, group, day, time, type, cell.text)

        self.save_on_disk()
        driver.close()

    def faculties(self):
        return self.data

    def kafs(self, users, from_id):
        return self.data[users.get(from_id, 'faculty')]

    def groups(self, users, from_id):
        return self.data[users.get(from_id, 'faculty')][users.get(from_id, 'kafedra')]

    def days(self, users, from_id):
        return self.data[users.get(from_id, 'faculty')][users.get(from_id, 'kafedra')][users.get(from_id, 'group')]

    def xxx(self, users, from_id, day):
        return \
        self.data[users.get(from_id, 'faculty')][users.get(from_id, 'kafedra')][users.get(from_id, 'group')][day]
