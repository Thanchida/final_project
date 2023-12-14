# try wrapping the code below that reads a persons.csv file in a class and make it more general such that it can read in any csv file

import csv, os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


class Read:
    def read_file(self, file_name, table_name):
        with open(os.path.join(__location__, file_name)) as f:
            rows = csv.DictReader(f)
            data = []
            for r in rows:
                data.append(dict(r))
        return Table(table_name,data)


# add in code for a Database class
class DB:
    def __init__(self):
        self.database = []

    def insert(self, table):
        self.database.append(table)

    def search(self, table_name):
        for table in self.database:
            if table.table_name == table_name:
                return table
        return None

    def get_table_column(self, table_name):
        for table in self.database:
            if table.table_name == table_name:
                return list(table.table[0].keys())

    def get_all_table(self):
        return [table.table_name for table in self.database]

    def get_table_data(self, table_name):
        for table in self.database:
            if table.table_name == table_name:
                return table.table
        return None



# add in code for a Table class
class Table:
    def __init__(self, table_name, table):
        self.table_name = table_name
        self.table = table

    def join(self, other_table, common_key):
        joined_table = Table(self.table_name + '_joins_' + other_table.table_name, [])
        for item1 in self.table:
            for item2 in other_table.table:
                if item1[common_key] == item2[common_key]:
                    dict1 = copy.deepcopy(item1)
                    dict2 = copy.deepcopy(item2)
                    dict1.update(dict2)
                    joined_table.table.append(dict1)
        return joined_table

    def filter(self, condition):
        filtered_table = Table(self.table_name + '_filtered', [])
        for item1 in self.table:
            if condition(item1):
                filtered_table.table.append(item1)
        return filtered_table

    def __iter__(self):
        return iter(self.table)

    def select(self, attributes_list):
        temps = []
        for item1 in self.table:
            dict_temp = {}
            for key in item1:
                if key in attributes_list:
                    dict_temp[key] = item1[key]
            temps.append(dict_temp)
        return temps

    def append(self, item):
        self.table.append(item)

    def update(self, func, key, val):
        filter_table = self.filter(func)
        if filter_table:
            for row in filter_table:
                row[key] = val

    def delete(self, func, key, val):
        filter_table = self.filter(func)
        if filter_table:
            for row in filter_table:
                if key in row and row[key] == val:
                    filter_table.table.remove(row)

    def __str__(self):
        return str(self.table)

# modify the code in the Table class so that it supports the insert operation where an entry can be added to a list of dictionary

# modify the code in the Table class so that it supports the update operation where an entry's value associated with a key can be updated
