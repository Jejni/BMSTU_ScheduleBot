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
