# **Final project for 2023's 219114/115 Programming I**

## **list of files in final project repo**
- ### **project_manage.py**
    - **'System' class**
      - this class is designed to handle different types of users with specific roles (e.g., students, faculty, admin) 
      and allows them to interact with the system through role-specific menus. The user data and project data are saved
      in CSV files upon logout.
    - #### **'User' class**
      - provides a way to retrieve the username associated with a given user ID from the 'login' table in the database.
    - #### **'Student' class**
      - This class is designed to handle various actions and functionalities related to a student's role, such as 
      creating a project, responding to project invitations
    - #### **'Lead' class**
      - perform actions specific to an lead's responsibilities, such as managing project members, inviting advisors, 
      modifying the project, and submitting 
      the project for evaluation.
    - #### **'Member' class**
      - perform actions specific to an member's responsibilities, such as checking project status, reviewing responses 
      from both students and faculty, modifying the project.
    - #### **'Advisor' class**
      - perform actions specific to an advisor's responsibilities, such as evaluating projects(excluding the advisor's own project),
      responding to requests from leads, and managing the evaluation process.
    - #### **'Project' class**
      -  a representation of individual projects within a project management system. It encapsulates methods for 
      accessing, modifying, and saving project details. 
    - #### **'Admin' class**
      - perform actions specific to an admin's responsibilities, such as manage users, including listing users, adding 
      new students and faculty, and deleting existing users from the system.
    - #### **'Faculty' class**
      - perform actions specific to an faculty's responsibilities, such as manage project requests, evaluate projects, 
      and respond to evaluation requests within the system.
- ### **database.py**
    - #### **'Read' class**
      - this class is to encapsulate the functionality of reading data from a CSV file and converting it into a format 
      that can be used within the program.
    - #### **'DB' class**
      - Managing tables within an in-memory database. It allows for inserting tables, searching for specific tables, 
      retrieving column names, getting a list of all tables, and fetching table data.
    - #### **'Table' class**
      - This class provides a set of methods to manipulate and operate on an in-memory table, offering functionality for 
      common database operations such as joining, filtering, selecting, appending, updating, and deleting rows.
- ### **project.csv**
    - A table with information about projects.
- ### **member_pending_request.csv**
    - A table with information about inviting members.
- ### **advisor_pending_request.csv**
    - A table with information about inviting advisors.
- ### **evaluate_request.csv**
    - A table with information about inviting evaluators.

## **How to compile and run**
- ### **project_manage.py(main program)**
- ### **Files Needed to Run the Main Program**
    - database.py
    - project.csv
    - member_pending_request.csv
    - advisor_pending_request.csv
    - evaluate_request.csv
    - login.csv
    - persons.csv
- ### **Run program**
```ruby
# Initialize the system
initialize()

# Create an object of the System class
system = System()

# Run the system
system.run()
```
- ### **Output**
```ruby
-------WELCOME-------
username: # Enter username
password: # Enter password
```

## **Role-Based Actions and Code Completion Percentage**
| Role    | Action                                     | Method                                                       | Class            | Completion percentage |
|---------|--------------------------------------------|--------------------------------------------------------------|------------------|-----------------------|
| Admin   | Add new student                            | add_new_student                                              | Admin            | 100%                  |
| Admin   | Add new faculty                            | add_new_faculty                                              | Admin            | 100%                  |
| Admin   | Delete student                             | delete_student                                               | Admin            | 100%                  |
| Admin   | Delete faculty                             | delete_faculty                                               | Admin            | 100%                  |
| Admin   | Report list of leads, members, advisors    | admin_menu                                                   | Admin            | 100%                  |
| Student | Create project                             | create_project                                               | student          | 100%                  |
| Student | Check invitation request                   | student_check_request                                        | Student          | 100%                  |
| Student | Response invitation                        | student_response                                             | Student          | 100%                  |
| Lead    | Send invitation to members                 | invite_member, check_member_availability, get_more_member    | Lead             | 100%                  |
| Lead    | Send invitation to members                 | invite_advisor, check_advisor_availability, get_more_advisor | Lead             | 100%                  |
| Lead    | Check student response                     | check_student_response                                       | Lead             | 100%                  |
| Lead    | Check faculty response                     | check_faculty_response                                       | Lead             | 100%                  |
| Lead    | Submit project                             | submit_project                                               | Lead             | 100%                  |
| Lead    | Check Project status                       | get_project, get_project_data                                | Lead, Project    | 100%                  |
| Lead    | Modify project                             | modify_project                                               | Project          | 100%                  |
| Member  | Check Project status                       | get_project, get_project_data                                | Member, Project  | 100%                  |
| Member  | Check student response                     | check_student_response                                       | Member           | 100%                  |
| Member  | Check faculty response                     | check_faculty_response                                       | Member           | 100%                  |
| Member  | Modify project                             | modify_project                                               | Project          | 100%                  |
| Faculty | Check invitation request                   | faculty_check_request, accept_more_request                   | Faculty          | 100%                  |
| Faculty | Response invitation                        | faculty_response                                             | Faculty          | 100%                  |
| Faculty | Check Project status                       | get_project_data                                             | Project          | 100%                  |
| Faculty | Check invitation to be evaluator           | see_request_for_evaluate                                     | Faculty          | 100%                  |
| Faculty | Evaluation                                 | evaluation, approve_project                                  | Faculty          | 100%                  |
| Advisor | Modify project                             | modify_project                                               | Project          | 100%                  |
| Advisor | Check invitation request for other project | faculty_check_request, accept_more_request                   | Advisor          | 100%                  |
| Advisor | Response invitation for other project      | faculty_response                                             | Advisor          | 100%                  |
| Advisor | Check Project status                       | get_project, get_project_data                                | Advisor, Project | 100%                  |
| Advisor | Check invitation to be evaluator           | see_request_for_evaluate                                     | Advisor          | 100%                  |
| Advisor | Evaluation                                 | evaluation, approve_project                                  | Advisor          | 100%                  |
| Advisor | Check evaluator response                   | check_evaluator_response                                     | Advisor          | 100%                  |

## **List of Missing Features and Outstanding Bugs**
- Users can't change their passwords.
- If a lead decides to create a project, they can't cancel it.
