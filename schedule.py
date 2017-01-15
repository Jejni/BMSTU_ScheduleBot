import lxml.html as html
import urllib.request
from selenium import webdriver
import re
import pprint

url = 'http://www.bmstu.ru/mstu/undergraduate/schedule'
page = urllib.request.urlopen(url).read()
page = html.fromstring(page)
page = page.findall(".//*[@class='row vt-listgroup']/div/table/tbody/tr/td/a")
urls = []
for element in page:
    urls.append(url + element.attrib['href'])

driver = webdriver.PhantomJS()
driver.get(urls[0])
page = html.fromstring(driver.page_source)
driver.close()

table = page.find(".//*[@class='wtHolder ht_master']/div/div/table/tbody")

firstrow = True

myd = {}
save_to_later = []

all_prop = {}
new_prop = {}


def add_to_dict(*args):
    if len(args) == 3:
        faculty, kaf, group = args[0], args[1], args[2]
        if faculty in myd:
            if kaf in myd[faculty]:
                myd[faculty][kaf][group] = {}
            else:
                myd[faculty][kaf] = {group: {}}
        else:
            myd[faculty] = {kaf: {group: {}}}
    if len(args) == 7:
        faculty, kaf, group, day, time, type, what = args[0], args[1], args[2], args[3], args[4], args[5], args[6]
        if day in myd[faculty][kaf][group]:
            if time in myd[faculty][kaf][group][day]:
                myd[faculty][kaf][group][day][time][type] = what
            else:
                myd[faculty][kaf][group][day][time] = {type: what}
        else:
            myd[faculty][kaf][group][day] = {time: {type: what}}


def clean_me(row):
    for cell in row:
        if 'style' in cell.attrib and cell.attrib['style'] == 'display: none;':
            # print('Test_clean_me_remove_before: ')
            print_row(row)
            row.remove(cell)
            # print('Test_clean_me_remove_after: ')
            print_row(row)
            clean_me(row)
            return row
    return row


def clean_me_all_prop():
    for key in all_prop.keys():
        cell = all_prop[key]
        if int(cell.attrib['rowspan']) in [0, 1]:
            del all_prop[key]
            clean_me_all_prop()
            return


def print_row(row):
    cells = 0
    for cell in row:
        print('Cell: ', cells)
        print(cell.attrib)
        print(cell.text)
        cells += 1


# doneeeeeeeeeeee


def build_full_row(row):
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

    clean_me_all_prop()

    return row


days = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']


def scan_prop(row):
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

    row = build_full_row(row)

    all_prop.update(new_prop)
    new_prop.clear()

    # print_row(row)

    return row


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
            add_to_dict(group[0][0], group[0][1], group[1])
            save_to_later.append(group)
        firstrow = False
        continue

    row = scan_prop(row)
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
            add_to_dict(faculty, kaf, group, day, time, type, cell.text)

# ("fuck")
pprint.pprint(myd)
