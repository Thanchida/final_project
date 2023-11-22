# import database module
import csv

from database import DB, Table, Read
database = DB()


# define a function called initializing
def initializing():

    # here are things to do in this function:

    # create an object to read all csv files that will serve as a persistent state for this program
    read_csv = Read()
    login_table = read_csv.read_file('login.csv','login')
    person_table = read_csv.read_file('persons.csv', 'persons')
    # create all the corresponding tables for those csv files
    # see the guide how many tables are needed
    # add all these tables to the database
    database.insert(login_table)
    database.insert(person_table)


# define a function called login
def login():
    # here are things to do in this function:
    # add code that performs a login task
    # ask a user for a username and password

    username = input('username: ')
    password = input('password: ')

    # returns [ID, role] if valid, otherwise returning None
    for i in database.search('login'):
        if username == i['username'] and password == i['password']:
            return [i['ID'], i['role']]
    return None


# define a function called exit
def exit():

    # here are things to do in this function:
    # write out all the tables that have been modified to the corresponding csv files
    # By now, you know how to read in a csv file and transform it into a list of dictionaries. For this project, you also need to know how to do the reverse, i.e., writing out to a csv file given a list of dictionaries. See the link below for a tutorial on how to do this:
   
    # https://www.pythonforbeginners.com/basics/list-of-dictionaries-to-csv-in-python
    my_file = open('reverse.csv', 'w')
    writer = csv.writer(my_file)
    writer.writerow(['ID', 'username', 'password', 'role'])
    for dictionary in database.search('login'):
        writer.writerow(dictionary.values())
    my_file.close()
    my_file = open('reverse.csv', 'r')
    print("The content of the csv file is:")
    print(my_file.read())
    my_file.close()


# make calls to the initializing and login functions defined above

initializing()
val = login()
print(val)

# based on the return value for login, activate the code that performs activities according to the role defined for that person_id

# if val[1] = 'admin':
    # see and do admin related activities
# elif val[1] = 'student':
    # see and do student related activities
# elif val[1] = 'member':
    # see and do member related activities
# elif val[1] = 'lead':
    # see and do lead related activities
# elif val[1] = 'faculty':
    # see and do faculty related activities
# elif val[1] = 'advisor':
    # see and do advisor related activities

# once everything is done, make a call to the exit function
exit()
