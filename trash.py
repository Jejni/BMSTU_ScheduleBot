class schedule:
    data = {'ИУ': {'3': {'31': {'чс': {'monday': {'12:00': 'You are free :3'}}}},
                   '1': {'11': {'чс': {
                       'sunday': {'8:30': 'You are free :3dgdfgdfgdfgdgdfgdfgdgsdgsg',
                                  '10:15': 'Networks',
                                  '12:15': 'Math'
                                  },
                       'monday': {'12:00': 'You are free :3'},
                       'tuesday': {'12:00': 'You are free :3',
                                   '10:15': 'Networks',
                                   '12:15': 'Math'
                                   },
                       'wednesday': {'12:00': 'You are free :3'},
                       'thursday': {'12:00': 'You are free :3'},
                       'friday': {'12:00': 'You are free :3'},
                       'saturday': {'12:00': 'You are free :3'}
                   },
                       'зн': {'monday': {'12:00': 'You are free :3'}},
                   },
                       '22': {'чс': {'monday': {'12:00': 'You are free :3'}}},
                       '12': {'чс': {'monday': {'12:00': 'You are free :3'}}},
                       '21': {'чс': {'monday': {'12:00': 'You are free :3'}}},
                       '31': {'чс': {'monday': {'12:00': 'You are free :3'}}},
                   },
                   '2': {'31': {'чс': {'monday': {'12:00': 'You are free :3'}}}},
                   '4': {'31': {'чс': {'monday': {'12:00': 'You are free :3'}}}},
                   '5': {'31': {'чс': {'monday': {'12:00': 'You are free :3'}}}},
                   },
            'МТ': {'4': {'31': {'чс': {'monday': {'12:00': 'You are free :3'}}}}},
            'Э': {'5': {'31': {'чс': {'monday': {'12:00': 'You are free :3'}}}}},
            'ИБМ': {'22': {'31': {'чс': {'monday': {'12:00': 'You are free :3'}}}}},
            'РЛ': {'6': {'31': {'чс': {'monday': {'12:00': 'You are free :3'}}}}}}

    def faculties(self):
        return self.data

    def kafs(self, from_id):
        return self.data[users.get(from_id, 'faculty')]

    def groups(self, from_id):
        return self.data[users.get(from_id, 'faculty')][users.get(from_id, 'kafedra')]

    def days(self, from_id):
        return self.data[users.get(from_id, 'faculty')][users.get(from_id, 'kafedra')][users.get(from_id, 'group')][
            'чс']

    def xxx(self, from_id, day):
        return self.data[users.get(from_id, 'faculty')][users.get(from_id, 'kafedra')][users.get(from_id, 'group')][
            'чс'][day]