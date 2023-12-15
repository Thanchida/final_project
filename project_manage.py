# import database module
import csv
import random

from database import DB, Read

database = DB()


def initialize():
    # create an object to read all csv files that will serve as a persistent state for this program
    read_csv = Read()

    # create all the corresponding tables for those csv files
    table_login = read_csv.read_file('login.csv', 'login')
    person_table = read_csv.read_file('persons.csv', 'persons')
    table_project = read_csv.read_file('project.csv', 'project')
    member_pending_request_table = read_csv.read_file('member_pending_request.csv', 'member_pending_request')
    advisor_pending_request_table = read_csv.read_file('advisor_pending_request.csv', 'advisor_pending_request')
    evaluate_request_table = read_csv.read_file('evaluate_request.csv', 'evaluate_request')

    # add all these tables to the database
    database.insert(table_project)
    database.insert(table_login)
    database.insert(person_table)
    database.insert(advisor_pending_request_table)
    database.insert(member_pending_request_table)
    database.insert(evaluate_request_table)


class System:
    def __init__(self):
        self.database = DB()
        self.current_user = None

    def login(self):
        # Ask a user for a username and password.
        login_table = database.search('login')
        while True:
            print('-------WELCOME-------')
            username = input('username: ')
            password = input('password: ')

            # returns [ID, role] if valid, otherwise returns None.
            for i in login_table.table:
                if username == i['username'] and password == i['password']:
                    return [i['ID'], i['role']]
            print('Username or password not correct. Please log in again.')

            # If username or password not correct ask user to try again.
            choice = input('Do you want to try again? (y/n): ')
            if choice != 'y':
                return None

    def login_menu(self, user_id, username, user_role):
        # loads the user's data based on their role and navigates to the respective menu associated with role.
        if user_role == 'student':
            self.current_user = Student(user_id, username, user_role)
            response = self.current_user.menu()

            # If user_role change during process the method recursively calls itself with the updated user_role.
            if response == 'lead':
                user_role = 'lead'
            if response == 'member':
                user_role = 'member'
            if response != 'exit':
                self.login_menu(user_id, username, user_role)
        elif user_role == 'lead':
            self.current_user = Lead(user_id, username, user_role)
            self.current_user.lead_menu()
        elif user_role == 'member':
            self.current_user = Member(user_id, username, user_role)
            self.current_user.member_menu()
        elif user_role == 'faculty':
            self.current_user = Faculty(user_id, username, user_role)
            self.current_user.faculty_menu()
        elif user_role == 'admin':
            self.current_user = Admin()
            self.current_user.admin_menu()
        elif user_role == 'advisor':
            self.current_user = Advisor(user_id, username, user_role)
            self.current_user.advisor_menu()

    def logout(self):
        # Save user and project data before logout
        for table_name in database.get_all_table():
            data_exists = database.get_table_data(table_name)
            if data_exists:
                my_file = open(f'{table_name}.csv', 'w', newline='')
                writer = csv.writer(my_file)
                table_column = database.get_table_column(table_name)
                writer.writerow(table_column)
                for row in database.search(table_name):
                    writer.writerow(row.values())
                my_file.close()

    def run(self):
        while True:
            user_id, user_role = self.login()
            # Get the username
            username = database.search('login').filter(lambda x: x['ID'] == user_id).select('username')[0]['username']

            # Call the login method to set the current user
            self.login_menu(user_id, username, user_role)
            choose = input('Do you want to change user? (y/n) ')
            if choose in ('n', 'N'):
                self.logout()
                break


class User:
    def __init__(self, user_id, username, user_role):
        self.user_id = user_id
        self.username = username
        self.user_role = user_role

    def find_name(self, find_id):
        # Get username
        login_table = database.search('login')
        return login_table.filter(lambda x: x['ID'] == find_id).select('username')[0]['username']


class Student(User):
    def __init__(self, user_id, username, user_role):
        super().__init__(user_id, username, user_role)
        self.user_id = user_id
        self.username = username
        self.user_role = user_role
        self.pending_num = 0
        self.project_id = ''
        self.project = Project(database.search('project'))
        self.title = ''
        self.lead = ''

    def menu(self):
        login_table = database.search('login')
        while True:
            print('------STUDENT MENU------')
            print('1. Create Project')
            print('2. See Request')
            print('3. Log out.')
            choice = int(input('Enter your choice: '))
            if choice == 1:
                # Change the role of a student who wants to create a project to 'lead'.
                for i in login_table:
                    if self.user_id == i['ID']:
                        i['role'] = 'lead'
                self.create_project()
                return 'lead'
            elif choice == 2:
                if self.student_check_request():
                    return 'member'
                return 'student'
            elif choice == 3:
                return 'exit'

    def create_project(self):
        print('Creating Project....')
        login_table = database.search('login')
        pending_table = database.search('member_pending_request')
        project_table = database.search('project')
        lead = login_table.filter(lambda x: x['ID'] == self.user_id).select('username')[0]['username']
        # Change the role of a student who wants to create a project to 'lead'.
        login_table.update(lambda x: x['ID'] == self.user_id, 'role', 'lead')

        # If another lead invites them to another project, change the status's value from 'waiting' to 'Deny'.
        for i in pending_table:
            if i['to_be_member'] == self.user_id and i['status'] == 'waiting':
                pending_table.update(lambda x: x['to_be_member'] == self.user_id, 'status', 'Deny')
        title = input('Interested in working on which project?: ')
        project_id = random.randint(1000, 9999)
        self.project_id = project_id
        self.title = title

        # Append the new project to the project_table in memory
        project_table.table.append({
            'project_id': self.project_id,
            'title': self.title,
            'lead': lead,
            'member_1': '',
            'member_2': '',
            'advisor': '',
            'status': 'Processing',
            'comment': ''
        })

    def student_check_request(self):
        pending_member = database.search('member_pending_request')
        accepted_response = False
        no_request = True
        for i in pending_member:
            if i['to_be_member'] == str(self.user_id) and i['status'] == 'waiting':
                no_request = False
                print(f'{i["lead"]} has invite you to join the project on the topic of "{i["title"]}".')
                accepted_response = self.student_response(i["lead"], i["title"])
                if accepted_response:
                    accepted_response = True
                    return accepted_response
        if no_request:
            print('!!! You have no request.!!!')
            return accepted_response

    def student_response(self, lead, title):
        login_table = database.search('login')
        pending_member = database.search('member_pending_request')
        project_table = database.search('project').filter(lambda x: x['title'] == title and x['lead'] == lead)
        accepted = False
        choice = input('Enter your response(y/n): ')
        if choice == 'y':
            print('Accept Success')
            print(f'You already be a member of {title} project')

            # update status from 'waiting' to 'Accept'
            pending_member.update(lambda x: x['to_be_member'] == self.user_id and x['lead'] == lead, 'status', 'Accept')
            # update status of project that student doesn't choose to be 'Deny'
            pending_member.update(lambda x: x['to_be_member'] == self.user_id and x['lead'] != lead, 'status', 'Deny')
            # change role form 'student' to 'member'
            login_table.update(lambda x: x['ID'] == self.user_id, 'role', 'member')

            # update member to project-table
            for i in project_table:
                # check that member_1 is empty or not
                if i['member_1'] == '':
                    # If empty, update the project table with the current user as member_1
                    project_table.update(lambda x: x['title'] == title and x['lead'] == lead, 'member_1', self.username)
                else:
                    # If not empty, update the project table with the current user as member_2
                    project_table.update(lambda x: x['title'] == title and x['lead'] == lead, 'member_2', self.username)
            accepted = True
            return accepted
        elif choice == 'n':
            print('Deny Success')
            # update status from 'waiting' to 'Deny'
            pending_member.update(lambda x: x['to_be_member'] == self.user_id and x['lead'] == lead, 'status', 'Deny')
            return accepted


class Lead(Student):
    def __init__(self, user_id, username, user_role):
        super().__init__(user_id, username, user_role)
        self.user_id = user_id
        self.username = username
        self.user_role = user_role
        self.pending_num = 0
        self.project_id = None
        self.project = None
        self.title = ''
        self.lead = ''

    def lead_menu(self):
        self.project = Project(database.search('project').filter(lambda x: x['lead'] == self.username))
        self.project_id = self.project.project_id
        while True:
            try:
                print('--------LEAD MENU--------')
                print('1. Check project status')
                print('2. Check response')
                print('3. Send member request')
                print('4. Send advisor request')
                print('5. Modify project')
                print('6. Submit project')
                print('99. Log off')
                choice = int(input('Enter your choice: '))
                if choice not in (1, 2, 3, 4, 5, 6, 99):
                    print('Try again! Invalid choice.')
                elif choice == 1:
                    self.get_project().get_project_data(self.project_id)
                elif choice == 2:
                    print('1. Check student response')
                    print('2. Check faculty response')
                    num = int(input('Enter number: '))
                    if num == 1:
                        self.check_student_response()
                    elif num == 2:
                        self.check_faculty_response()
                elif choice == 3:
                    self.invite_member()
                elif choice == 4:
                    self.invite_advisor()
                elif choice == 5:
                    self.project.modify_project(self.project_id)
                elif choice == 6:
                    self.submit_project()
                elif choice == 99:
                    break
            except ValueError:
                print('Invalid input. Please enter a number.')

    def get_project(self):
        return self.project

    def invite_member(self):
        project_table = database.search('project').filter(lambda x: x['lead'] == self.username)
        pending_table = database.search('member_pending_request')
        while True:
            # Check that if two students have already been invited, additional invitations cannot be sent.
            if not self.get_more_member():
                print("You've successfully invited all members...")
                break

            # Print the list of students you can invite, considering those who have not accepted other projects,
            # have not been invited yet, and have denied your project.
            uninvited = self.check_member_availability()
            for u in uninvited:
                print(u)
            print('-----------------------')
            print('Whom would you like to invite to participate in the project?')
            member_id = input('Enter ID: ')

            # Iterate through each project in the project table and Check if the current user is the lead of the project
            for j in project_table:
                if j['lead'] == self.username:
                    # If yes, update the project_id and title attributes
                    self.project_id = j['project_id']
                    self.title = j['title']

            # Append a new entry to the pending table and set default of status to 'waiting'
            pending_table.table.append(
                {'project_id': self.project_id, 'title': self.title, 'lead': self.username, 'to_be_member': member_id,
                 'status': 'waiting'})
            print(f'Request {member_id} Success.')
            choose = input('Do you want to request more?(y/n): ')
            if choose == 'n':
                break

    def get_more_member(self):
        # This function is designed to prevent students from accepting invitations simultaneously,
        # ensuring that invitations are not sent to more than two people.
        pending_member = database.search('member_pending_request').filter(lambda x: x['lead'] == self.username)
        num = 0
        for i in pending_member:
            if i['status'] == 'waiting':
                num += 1
            elif i['status'] == 'Accept':
                num += 1
        # Return it as a boolean
        return num < 2

    def check_member_availability(self):
        students = database.search('login').filter(lambda x: x['role'] == 'student')
        pending_table = database.search('member_pending_request')
        uninvited = []

        # Check if the student has been invited or has accepted an invitation for the current project
        for student in students:
            invited = False
            for member in pending_table:
                if ((student['ID'] == member['to_be_member']
                     and member['project_id'] == self.project_id)
                        or (student['ID'] == member['to_be_member'] and member['status'] == 'Accept')):
                    invited = True
                    break

            # If the student has not been invited, add their information to the list
            if not invited:
                uninvited.append(f"{student['username'].ljust(15)} {student['ID']}")
        return uninvited

    def get_more_advisor(self):
        # This function is designed to prevent faculties from accepting invitations simultaneously,
        # ensuring that invitations are not sent to more than one people.
        pending_advisor = database.search('advisor_pending_request').filter(lambda x: x['project_id'] == self.project_id)
        num = 0
        for i in pending_advisor:
            if i['status'] == 'waiting':
                num += 1
            elif i['status'] == 'Accept':
                num += 1
        # Return it as a boolean
        return num < 1

    def check_student_response(self):
        pending_member = database.search('member_pending_request').filter(lambda x: x['project_id'] == self.project_id)
        print('pending_member', pending_member)
        print('---STUDENT RESPONSE---')
        for i in pending_member.table:
            print('username: ', self.find_name(i['to_be_member']))
            print('user_id: ', i['to_be_member'])
            print('status: ', i['status'])
            print('---------------------')

        # Check if any student responded with 'Deny'
        for j in pending_member.table:
            if j['status'] == 'Deny':
                # Check if there is room to invite more members (less than 2 members invited)
                if self.get_more_member() < 2:
                    # Ask lead to decide whether to request more student or not
                    choose = input('Do you want to request more?(y/n): ')
                    if choose == 'y':
                        self.invite_member()
                        break

    def invite_advisor(self):
        project_table = database.search('project').filter(lambda x: x['lead'] == self.username)
        pending_table = database.search('advisor_pending_request')
        while True:
            if not self.get_more_advisor():
                print("Can't invite more advisor.")
                break
            # Print the list of faculties you can invite, considering those who have not been invited yet.
            uninvited = self.check_advisor_availability()
            for u in uninvited:
                print(u)
            print('-----------------------')
            print('Whom would you like to invite to be an advisor of the project?')
            advisor_id = input('Enter ID: ')

            # Iterate through each project in the project table and Check if the current user is the lead of the project
            for j in project_table:
                # If yes, update the project_id and title attributes
                self.project_id = j['project_id']
                self.title = j['title']
            # Append a new entry to the pending table and set default of status to 'waiting'
            pending_table.table.append(
                {'project_id': self.project_id, 'title': self.title, 'lead': self.username, 'to_be_advisor': advisor_id,
                 'status': 'waiting'})
            print(f'Request {advisor_id} Success.')
            choose = input('Do you want to request more?(y/n): ')
            if choose == 'n':
                break

    def check_advisor_availability(self):
        faculties = database.search('login').filter(lambda x: x['role'] == 'faculty' or x['role'] == 'advisor')
        pending_table = database.search('advisor_pending_request')
        uninvited = []
        for faculty in faculties:
            invited = False

            # Check if the faculty member has been invited, accepted, or denied an invitation for the current project.
            for j in pending_table:
                if faculty['ID'] == j['to_be_advisor'] and j['status'] == 'Accept' and j['lead'] == self.username or\
                        faculty['ID'] == j['to_be_advisor'] and j['status'] == 'Deny' and j['lead'] == self.username:
                    invited = True
                    break

            # If the faculty member has not been invited, accepted, or denied, add their information to the list.
            if not invited:
                uninvited.append(f"{faculty['username'].ljust(15)} {faculty['ID']}")
        return uninvited

    def check_faculty_response(self):
        pending_advisor = database.search('advisor_pending_request').filter(lambda x: x['lead'] == self.username)
        print('---FACULTY RESPONSE---')
        for i in pending_advisor:
            print('username: ', self.find_name(i['to_be_advisor']))
            print('user_id: ', i['to_be_advisor'])
            print('status: ', i['status'])
            print('---------------------')

        # Check if any student responded with 'Deny'
        for j in pending_advisor:
            if j['status'] == 'Deny':
                # Check if there is room to invite more faculty (less than 1 faculty invited)
                if self.get_more_advisor():
                    choose = input('Do you want to request more?(y/n): ')
                    if choose == 'y':
                        self.invite_advisor()

    def submit_project(self):
        project_table = database.search('project').filter(lambda x: x['lead'] == self.username)
        # Check that the project has obtained all the required members and the advisor
        for project in project_table:
            if (project['member_1'] != '' and project['member_2'] != '' and project['advisor'] != ''
                    and project['comment'] != ''):
                submit = input('Enter to submit project: ')
                if submit == '':
                    # Change status from 'Processing' to 'waiting for evaluation'
                    project_table.update(lambda x: x['lead'] == self.username, 'status', 'waiting for evaluation')
                    print('submit successfully.')
            else:
                print('Your project not ready to submit.')


class Member(Lead):
    def __init__(self, user_id, username, user_role):
        super().__init__(user_id, username, user_role)
        self.user_id = user_id
        self.username = username
        self.user_role = user_role
        self.pending_num = 0
        self.project_id = ''
        self.project = None
        self.title = ''
        self.lead = ''

    def member_menu(self):
        self.project = Project(database.search('project').filter(lambda x: x['member_1'] == self.username or
                                                                 x['member_2'] == self.username))
        self.project_id = self.project.project_id
        while True:
            try:
                print('-------MEMBER MENU-------')
                print('1. Check project status')
                print('2. Check response')
                print('3. Modify project')
                print('99. Log out')
                choice = int(input('Enter your choice: '))
                if choice not in (1, 2, 3, 99):
                    print('Try again! Invalid choice.')
                elif choice == 1:
                    self.get_project().get_project_data(self.project_id)
                elif choice == 2:
                    print('1. Check student response')
                    print('2. Check faculty response')
                    num = int(input('Enter number: '))
                    if num == 1:
                        self.check_student_response()
                    elif num == 2:
                        self.check_faculty_response()
                elif choice == 3:
                    self.project.modify_project(self.project_id)
                elif choice == 99:
                    break
            except ValueError:
                print('Invalid input. Please enter a number.')

    def get_project(self):
        return self.project

    def check_faculty_response(self):
        pending_advisor = database.search('advisor_pending_request').filter(lambda x: x['project_id'] == self.project_id)
        print('---FACULTY RESPONSE---')
        for i in pending_advisor.table:
            print('username: ', self.find_name(i['to_be_advisor']))
            print('user_id: ', i['to_be_advisor'])
            print('status: ', i['status'])
            print('---------------------')


class Advisor(User):
    def __init__(self, user_id, username, user_role):
        super().__init__(user_id, username, user_role)
        self.user_id = user_id
        self.username = username
        self.user_role = user_role
        self.pending_num = 0
        self.project_id = ''
        self.project = Project(database.search('project'))
        self.title = ''
        self.lead = ''

    def advisor_menu(self):
        while True:
            try:
                print('------ADVISOR MENU------')
                print('1. Check project status')
                print('2. Modify project')
                print('3. Invite faculty to evaluate')
                print('4. See request to be an advisor for other project')
                print('5. See request for evaluate')
                print('6. Evaluate project')
                print('99. Back to Log In')
                choice = int(input('Enter your choice: '))
                if choice not in (1, 2, 3, 4, 5, 6, 99):
                    print('Try again! Invalid choice.')
                elif choice == 1:
                    self.get_project().get_project_data(self.project_id)
                elif choice == 2:
                    self.project.modify_project(self.project_id)
                elif choice == 3:
                    self.invite_to_evaluate()
                elif choice == 4:
                    self.faculty_check_request()
                elif choice == 5:
                    self.see_request_for_evaluate()
                elif choice == 6:
                    self.approve_project()
                elif choice == 99:
                    break
            except ValueError:
                print('Invalid input. Please enter a number.')

    def get_project(self):
        return self.project

    def invite_to_evaluate(self):
        faculty_table = database.search('login').filter(lambda x: x['role'] == 'faculty' or x['role'] == 'advisor')
        project_table = database.search('project').filter(lambda x: x['advisor'] == self.username)
        evaluate_pending = database.search('evaluate_request')
        advisor_pending = database.search('advisor_pending_request').filter(lambda x: x['to_be_advisor'] == self.user_id and x['status'] == 'Accept')
        project = ''
        invited_faculty_ids = set()  # Keep track of invited faculty IDs
        if len(advisor_pending.table) > 1:
            project = input('What project you want to invite evaluator?(enter project_id): ')
        while True:
            if not self.get_more_evaluator(project):
                print("Can't invite more faculty.")
                break
            # Create a set to store usernames of advisors
            all_advisors = set(m['advisor'] for m in project_table if m['advisor'])

            # Filter out faculty members who are already advisors and not invited
            faculty_to_invite = [faculty for faculty in faculty_table.table if
                                 faculty['username'] not in all_advisors and faculty['ID'] not in invited_faculty_ids]
            for faculty in faculty_to_invite:
                print(f"{faculty['username'].ljust(15)} {faculty['ID']}")
            print('-----------------------')
            print('Whom would you like to invite to be an evaluator of the project?')
            faculty_id = input('Enter ID: ')

            # Check if faculty has already been invited
            if faculty_id in invited_faculty_ids:
                print(f'Faculty with ID {faculty_id} has already been invited. Please enter a different ID.')
                continue
            choose = input('Do you want to request more? (y/n): ')
            if choose.lower() == 'n':
                break

            # Add the faculty ID to the set of invited faculty
            invited_faculty_ids.add(faculty_id)

            for j in project_table:
                if j['project_id'] == project:
                    self.title = j['title']
                    self.lead = j['lead']

            evaluate_pending.table.append(
                {'project_id': project, 'title': self.title, 'lead': self.lead, 'to_be_evaluator': faculty_id,
                 'status': 'waiting', 'num_approve': int(0)})
            print(f'Request {faculty_id} Success.')

    def get_more_evaluator(self, project_id):
        # This function is designed to prevent advisors from accepting invitations simultaneously,
        # ensuring that invitations are not sent to more than two people.
        pending_evaluate = database.search('evaluate_request').filter(lambda x: x['project_id'] == project_id)
        num = 0
        for i in pending_evaluate:
            if i['status'] == 'waiting':
                num += 1
            elif i['status'] == 'Accept':
                num += 1
        # return as a boolean
        return num < 2

    def faculty_check_request(self):
        pending_advisor = database.search('advisor_pending_request').filter(lambda x: x['to_be_advisor']
                                                                            == str(self.user_id) and x['status']
                                                                            == 'waiting')
        project_table = database.search('project')
        accepted_response = False
        no_request = True
        for i in pending_advisor:
            no_request = False
            print(f'{i["lead"]} has invite you to join the project on the topic of "{i["title"]}".')
            accepted_response = self.faculty_response(i["lead"], i["title"])

            # If the faculty member accepts the request, update the project table
            if accepted_response:
                if self.project.advisor == '':
                    project_table.update(lambda x: x['advisor'] == '', 'advisor', self.username)
                if not self.accept_more_request():
                    accepted_response = True
                return accepted_response
        if no_request:
            print('!!! You have no request.!!!')
            return accepted_response

    def faculty_response(self, lead, title):
        login_table = database.search('login')
        pending_advisor = database.search('advisor_pending_request')
        project_table = database.search('project')
        accepted = False
        choice = input('Enter your response(y/n): ')
        if choice == 'y':
            print('Accept Success')
            print(f'You already be a advisor of {title} project')

            # Update status from 'waiting' to 'Accept'
            pending_advisor.update(lambda x: x['to_be_advisor'] == self.user_id and x['title'] == title, 'status', 'Accept')

            # Update role from 'faculty' to 'advisor'
            login_table.update(lambda x: x['ID'] == self.user_id, 'role', 'advisor')

            # Update advisor of the project
            project_table.update(lambda x: x['title'] == title, 'advisor', self.username)
            self.user_role = 'advisor'
            accepted = True
            return accepted
        elif choice == 'n':
            print('Deny Success')
            # Update status from 'waiting' to 'Deny'
            pending_advisor.update(lambda x: x['to_be_advisor'] == self.user_id and x['lead'] == lead, 'status', 'Deny')
            return accepted

    def accept_more_request(self):
        pending_advisor = database.search('advisor_pending_request').filter(lambda x: x['to_be_advisor']
                                                                            == str(self.user_id) and x['status']
                                                                            == 'Accept')
        num = 0
        # Count how many request accepted
        for i in pending_advisor.table:
            num += 1
        # return as a boolean
        return num < 3

    def see_request_for_evaluate(self):
        evaluate_pending = database.search('evaluate_request').filter(lambda x: x['to_be_evaluator'] == str(self.user_id))
        # default requests_exist to be false to check that the faculty have request or not
        requests_exist = False

        for i in evaluate_pending:
            requests_exist = True
            print(f'Advisor of {i["title"]} project invites you to be an evaluator')
            choose = input('Do you want to accept or deny? (y/n): ')
            if choose == 'y':
                # Update status from 'waiting' to 'Accept'
                evaluate_pending.update(lambda x: x['to_be_evaluator'] == self.user_id and x['title'] == i['title']
                                        , 'status', 'Accept')
            elif choose == 'n':
                # Update status from 'waiting' to 'Deny'
                evaluate_pending.update(lambda x: x['to_be_evaluator'] == self.user_id and x['title'] == i['title']
                                        , 'status', 'Deny')

        if not requests_exist:
            print('Not Have Request')
            return

    def evaluation(self):
        project_table = database.search('project')
        evaluate_table = database.search('evaluate_request')
        found_project = False
        id_to_evaluate = None

        # Display a list of available projects for evaluation
        print("List of available projects:")
        for project in evaluate_table:
            if project['to_be_evaluator'] == self.user_id and project['status'] == 'Accept':
                print(f"Project ID: {project['project_id']} - Title: {project['title']}")

        # Get the user's input for what project user want to evaluate
        user_input = input("Enter the project ID that you want to evaluate: ")
        self.project.get_project_data(user_input)
        for project in project_table:
            for evaluate_request in evaluate_table:
                if (
                        project['project_id'] == evaluate_request['project_id']
                        and evaluate_request['to_be_evaluator'] == self.user_id
                        and evaluate_request['status'] == 'Accept'
                        and project['project_id'] == user_input
                ):
                    id_to_evaluate = user_input
                    found_project = True

                    evaluate_decision = input('Approve this project? (y/n): ')
                    if evaluate_decision.lower() == 'y':
                        # Check if the project is not already approved
                        if project['status'] != 'Approve':
                            evaluate_request['num_approve'] = str(int(evaluate_request['num_approve']) + 2)
                            print('Thank you. Your evaluation was successful.')
                        else:
                            print('Project is already approved.')

                    elif evaluate_decision.lower() == 'n':
                        evaluate_request['num_approve'] = str(int(evaluate_request['num_approve']) + 1)
                        print('Thank you. Your evaluation was successful.')

                    break

        if not found_project:
            print(f"You don't have the project with ID {user_input} to evaluate.")
            return None

        return id_to_evaluate

    def approve_project(self):
        id = self.evaluation()
        # Check that have available project to evaluate or not
        if id is None:
            return None

        project_table = database.search('project')
        evaluate_table = database.search('evaluate_request')

        # Check that project has been evaluated by both of evaluators
        project_for_evaluate = evaluate_table.filter(lambda x: x['project_id'] == id and x['num_approve'] != str(0))

        num = 0
        # Sum up the number of approvals from both evaluators
        if len(project_for_evaluate.table) == 2:
            for evaluate_request in project_for_evaluate.table:
                num += int(evaluate_request['num_approve'])

        # Update the project status
        if num == 4:
            project_table.update(lambda x: x['project_id'] == id, 'status', 'Approve')
        elif num < 4:
            project_table.update(lambda x: x['project_id'] == id, 'status', 'Under Review')

        return None


class Project:
    def __init__(self, table):
        self.project_table = table
        for project in self.project_table:
            self.project_id = project['project_id']
            self.lead = project['lead']
            self.title = project['title']
            self.member_1 = project['member_1']
            self.member_2 = project['member_2']
            self.advisor = project['advisor']
            self.status = project['status']
        self.num_member = 0

    def project_table_template(self):
        return {'project_id': self.project_id, 'title': self.title, 'lead': self.lead, 'member_1': self.member_1,
                'member_2': self.member_2, 'advisor': self.advisor, 'status': self.status}

    def check_project_detail(self):
        project = database.search('project')
        print('---PROJECT DETAIL---')
        for i in project.table:
            print('project_id: ', i['project_id'])
            print('title: ', i['title'])
            print('lead: ', i['lead'])
            print('first member: ', i['member_1'])
            print('second member: ', i['member_2'])
            print('advisor: ', i['advisor'])
            print('status: ', i['status'])
            print('------------------')

    def modify_project(self, project_id):
        project_table = database.search('project')
        new_comment = input('Add comments on any problems you found in our project: ')
        print('In the process of modification.')
        project_table.update(lambda x: x['project_id'] == project_id, 'comment', new_comment)

    def get_project_data(self, project_id):
        for i in self.project_table:
            if i['project_id'] == project_id:
                self.project_id = i['project_id']
                self.title = i['title']
                self.lead = i['lead']
                self.member_1 = i['member_1']
                self.member_2 = i['member_2']
                self.advisor = i['advisor']
                self.status = i['status']
                print('-----PROJECT DATA-----')
                print('project_id: ', i['project_id'])
                print('title: ', i['title'])
                print('lead: ', i['lead'])
                print('first member: ', i['member_1'])
                print('second member: ', i['member_2'])
                print('advisor: ', i['advisor'])
                print('status: ', i['status'])
                print('------------------')

    def update_project_data(self):
        # Find the project in the project table and update its values
        for project in self.project_table.table:
            if project['project_id'] == self.project_id:
                project.update({
                    'title': self.title,
                    'lead': self.lead,
                    'member_1': self.member_1,
                    'member_2': self.member_2,
                    'advisor': self.advisor,
                    'status': self.status
                })
            break

    def save_project_data(self):
        # Save project data to persistent storage (e.g., CSV file)
        try:
            with open('project.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(
                    ['project_id', 'title', 'lead', 'member_1', 'member_2', 'advisor', 'status'])
                for project in self.project_table.table:
                    writer.writerow([
                        project['project_id'],
                        project['title'],
                        project['lead'],
                        project['member_1'],
                        project['member_2'],
                        project['advisor'],
                        project['status']
                    ])
        except FileNotFoundError:
            # Handle the case where the file does not exist
            pass


class Admin:

    def admin_menu(self):
        login_table = database.search('login')
        person_table = database.search('persons')
        members = []
        leads = []
        advisors = []
        while True:
            print('-----ADMIN MENU-----')
            print('1. List of members')
            print('2. List of leads')
            print('3. List of advisors')
            print('4. Add new student')
            print('5. Add new faculty')
            print('99. Back to Log In')
            choice = int(input('Enter your choice: '))
            if choice not in (1, 2, 3, 4, 5, 99):
                print('Try again! Invalid choice.')
            if choice == 1:
                # Display a list of members
                for i in login_table:
                    for j in person_table:
                        if i['ID'] == j['ID'] and i['role'] == 'member':
                            members.append(f"{j['fist'].ljust(4)} {j['last']}")
                if members:
                    print('This following list is a list of members:')
                    for member in members:
                        print(member)
                    print('-----------------')
                else:
                    print('No member found.')
            elif choice == 2:
                # Display a list of leads
                for i in login_table:
                    for j in person_table:
                        if i['ID'] == j['ID'] and i['role'] == 'lead':
                            leads.append(f"{j['fist'].ljust(4)} {j['last']}")
                if leads:
                    print('This following list is a list of leads:')
                    for lead in leads:
                        print(lead)
                    print('-----------------')
                else:
                    print('No lead found.')
            elif choice == 3:
                # Display a list of advisors
                for i in login_table:
                    for j in person_table:
                        if i['ID'] == j['ID'] and i['role'] == 'advisor':
                            advisors.append(f"{j['first'].ljust(4)} {j['last']}")
                if advisors:
                    print('This following list is a list of advisors:')
                    for advisor in advisors:
                        print(advisor)
                    print('-----------------')
                else:
                    print('No members found.')
            elif choice == 4:
                # Add a new student
                self.add_new_student()
            elif choice == 5:
                # Add a new faculty
                self.add_new_faculty()
            elif choice == 99:
                break

    def add_new_student(self):
        person_table = database.search('persons')
        login_table = database.search('login')
        first = input('Enter first name: ')
        last = input('Enter last name: ')
        password = random.randint(1000, 9999)
        id = random.randint(1000000, 9999999)
        username = f"{first}.{last[0]}"

        # Add new student to the 'person_table' and the 'login_table'.
        person_table.table.append({'ID': id, 'fist': first, 'last': last, 'type': 'student'})
        login_table.table.append({'ID': id, 'username': username, 'password': password, 'role': 'student'})
        print("Successfully add a new student.")

    def add_new_faculty(self):
        person_table = database.search('persons')
        login_table = database.search('login')
        first = input('Enter first name: ')
        last = input('Enter last name: ')
        password = random.randint(1000, 9999)
        id = random.randint(1000000, 9999999)
        username = f"{first}.{last[0]}"

        # Add new faculty to the 'person_table' and the 'login_table'.
        person_table.table.append({'ID': id, 'fist': first, 'last': last, 'type': 'faculty'})
        login_table.table.append({'ID': id, 'username': username, 'password': password, 'role': 'faculty'})
        print("Successfully add a new faculty.")


class Faculty(User):

    def __init__(self, user_id, username, user_role):
        super().__init__(user_id, username, user_role)
        self.user_id = user_id
        self.username = username
        self.user_role = user_role
        self.pending_num = 0
        self.project_id = ''
        self.project = Project(database.search('project'))
        self.title = ''
        self.lead = ''

    def faculty_menu(self):
        while True:
            print('-----FACULTY MENU-----')
            print('1. See Request')
            print('2. See Detail Project')
            print('3. Evaluate Project')
            print('4. See request for evaluate')
            print('99. Back to Log In')
            choose = int(input('Enter your choice: '))
            if choose not in (1, 2, 3, 4, 99):
                print('Try again! Invalid choice.')
            if choose == 1:
                self.faculty_check_request()
            elif choose == 2:
                project_id = input('Enter project_ID of project you want to see: ')
                self.project.get_project_data(project_id)
            elif choose == 3:
                self.approve_project()
            elif choose == 4:
                self.see_request_for_evaluate()
            elif choose == 99:
                break

    def faculty_check_request(self):
        pending_advisor = database.search('advisor_pending_request').filter(lambda x: x['to_be_advisor']
                                                                            == str(self.user_id) and x['status']
                                                                            == 'waiting')
        project_table = database.search('project')
        accepted_response = False
        no_request = True
        for i in pending_advisor:
            no_request = False
            print(f'{i["lead"]} has invite you to join the project on the topic of "{i["title"]}".')
            accepted_response = self.faculty_response(i["lead"], i["title"])

            # If the faculty member accepts the request, update the project table
            if accepted_response:
                if self.project.advisor == '':
                    project_table.update(lambda x: x['advisor'] == '', 'advisor', self.username)
                if not self.accept_more_request():
                    accepted_response = True
                return accepted_response
        if no_request:
            print('!!! You have no request.!!!')
            return accepted_response

    def faculty_response(self, lead, title):
        login_table = database.search('login')
        pending_advisor = database.search('advisor_pending_request')
        project_table = database.search('project')

        # Set the default value of accepted to be False to check the faculty response.
        accepted = False
        choice = input('Enter your response(y/n): ')
        if choice == 'y':
            print('Accept Success')
            print(f'You already be a advisor of {title} project')
            # Update the status from 'waiting' to 'Accept' in the pending advisor table
            pending_advisor.update(lambda x: x['to_be_advisor'] == self.user_id and x['title'] == title, 'status', 'Accept')

            # Update role from 'faculty' to 'advisor' in the login table
            login_table.update(lambda x: x['ID'] == self.user_id, 'role', 'advisor')

            # Update the advisor of the project in the project table
            project_table.update(lambda x: x['title'] == title, 'advisor', self.username)
            accepted = True
            return accepted
        elif choice == 'n':
            print('Deny Success')
            # Update the status from 'waiting' to 'Deny' in the pending advisor table
            pending_advisor.update(lambda x: x['to_be_advisor'] == self.user_id and x['lead'] == lead, 'status', 'Deny')
            return accepted

    def accept_more_request(self):
        pending_advisor = database.search('advisor_pending_request').filter(lambda x: x['to_be_advisor']
                                                                            == str(self.user_id) and x['status']
                                                                            == 'Accept')
        num = 0
        # Count how many request accepted
        for i in pending_advisor.table:
            num += 1
        # return as a boolean
        return num < 3

    def see_request_for_evaluate(self):
        evaluate_pending = database.search('evaluate_request').filter(lambda x: x['to_be_evaluator'] == str(self.user_id))
        # default requests_exist to be false to check that the faculty have request or not
        requests_exist = False

        for i in evaluate_pending:
            requests_exist = True
            print(f'Advisor of {i["title"]} project invites you to be an evaluator')
            choose = input('Do you want to accept or deny? (y/n): ')
            if choose == 'y':
                # Update status from 'waiting' to 'Accept'
                evaluate_pending.update(lambda x: x['to_be_evaluator'] == self.user_id and x['title'] == i['title']
                                        , 'status', 'Accept')
            elif choose == 'n':
                # Update status from 'waiting' to 'Deny'
                evaluate_pending.update(lambda x: x['to_be_evaluator'] == self.user_id and x['title'] == i['title']
                                        , 'status', 'Deny')

        if not requests_exist:
            print('Not Have Request')
            return

    def evaluation(self):
        project_table = database.search('project')
        evaluate_table = database.search('evaluate_request')
        found_project = False
        id_to_evaluate = None

        # Display a list of available project for evaluation
        print("List of available projects:")
        for project in evaluate_table:
            if project['to_be_evaluator'] == self.user_id and project['status'] == 'Accept':
                print(f"Project ID: {project['project_id']} - Title: {project['title']}")

        # Get the user's input for what project user want to evaluate
        user_input = input("Enter the project ID that you want to evaluate: ")
        self.project.get_project_data(user_input)
        for project in project_table:
            for evaluate_request in evaluate_table:
                if (
                        project['project_id'] == evaluate_request['project_id']
                        and evaluate_request['to_be_evaluator'] == self.user_id
                        and evaluate_request['status'] == 'Accept'
                        and project['project_id'] == user_input
                ):
                    id_to_evaluate = user_input
                    found_project = True

                    evaluate_decision = input('Approve this project? (y/n): ')
                    if evaluate_decision.lower() == 'y':
                        # Check if the project is not already approved
                        if project['status'] != 'Approve':
                            evaluate_request['num_approve'] = str(int(evaluate_request['num_approve']) + 2)
                            print('Thank you. Your evaluation was successful.')
                        else:
                            print('Project is already approved.')

                    elif evaluate_decision.lower() == 'n':
                        evaluate_request['num_approve'] = str(int(evaluate_request['num_approve']) + 1)
                        print('Thank you. Your evaluation was successful.')

                    break

        if not found_project:
            print(f"You don't have the project with ID {user_input} to evaluate.")
            return None

        return id_to_evaluate

    def approve_project(self):
        id = self.evaluation()
        # Check that have available project to evaluate or not
        if id is None:
            return None

        project_table = database.search('project')
        evaluate_table = database.search('evaluate_request')

        # Check that project has been evaluated by both of evaluators
        project_for_evaluate = evaluate_table.filter(lambda x: x['project_id'] == id and x['num_approve'] != str(0))

        num = 0
        # Sum up the number of approvals from both evaluators
        if len(project_for_evaluate.table) == 2:
            for evaluate_request in project_for_evaluate.table:
                num += int(evaluate_request['num_approve'])

        # Update the project status
        if num == 4:
            project_table.update(lambda x: x['project_id'] == id, 'status', 'Approve')
        elif num < 4:
            project_table.update(lambda x: x['project_id'] == id, 'status', 'Under Review')

        return None


# Initialize the system
initialize()

# Create an object of the System class
system = System()

# Run the system
system.run()
