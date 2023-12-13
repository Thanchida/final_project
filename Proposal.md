**ADMIN**
- Update table:
    - Add new student.
        - Add new student to the 'person.csv' file and the 'login.csv' file.
    - Add new faculty.
        - Add new faculty to the 'person.csv' file and the 'login.csv' file.
- Report data in the database:
    - List of current project leads.
    - List of current members.
    - List of current advisors.
        - Loop through the 'login.csv' file to find persons whose roles are lead, member, and advisor, and create lists.


**STUDENT**
- Choose to create project or not.
    - If a student chooses to create a project, change their role from 'student' to 'lead'.
    - If another lead invites them to another project (indicated by an ID in the to_be_member's value in the 'member_pending_request.csv' file), change the status's value from 'waiting' to 'Deny'.
- See pending invitations and choose to accept or deny them.
    - If a student chooses to accept an invitation, change their role from 'student' to 'member'.


**LEADER**
- Create a project.
    - The lead will enter a title.
    - Generate a random project_ID.
    - Set the default status of the project to 'Processing'.
- Invite students to be members.
    - Set a limit to allow only 2 student invitations. If a student denies an invitation, the lead can then invite more.
- Invite faculty to e advisors.
    - Set a limit to allow only 1 faculty invitation. If a faculty denies an invitation, the lead can then invite more.
- See details of the project.
    - Title.
    - Lead's name.
    - Member's name.
    - Advisor's name.
    - Status
    - Comment
- Modify the project(add comments on the desired modifications).
    - The lead will enter a comment.
- See pending invitations for members and advisors.
    - Loop through the 'member_pending_request.csv' file and the 'advisor_pending_request.csv' file to find the responses (accept or deny) from students and faculties.
- Submit the project.
    - Check that the project has obtained all the required members and the advisor then the lead can submit.


**MEMBER**
- See details of the project.
    - Title.
    - Lead's name.
    - Member's name.
    - Advisor's name.
    - Status
    - Comment
- Modify the project(add comments on desired modifications).
    - The member will enter a comment.
- See pending invitations for members and advisors.
    - Loop through the 'member_pending_request.csv' file and the 'advisor_pending_request.csv' file to find the responses (accept or deny) from students and faculties.


**FACULTY**
- See pending invitations for be an advisor of a project and choose to accept or deny.
    - If a faculty chooses to accept an invitation, change their role from 'faculty' to 'advisor'.
- See invitations to be an evaluator of project and choose to accept or deny.
    - The faculty will enter a response(accept/deny).
- See details of all projects.
    - The faculty will enter the project_ID of the project they want to see details of.
    - Title.
    - Lead's name.
    - Member's name.
    - Advisor's name.
    - Status
    - Comment
- Evaluate projects.
    - Choose whether to approve the project or not.
      - If approved, change the status of the project from 'wait for evaluation' to 'Approve'.
      - If not approved, change the status of the project from 'wait for evaluation' to 'Processing'.


**ADVISOR**
- See details of all projects.
    - The advisor will enter the project_ID of the project they want to see details of.
    - Title.
    - Lead's name.
    - Member's name.
    - Advisor's name.
    - Status
    - Comment
- See invitations to be an evaluator of other projects and choose to accept or deny (cannot be an evaluator of a project 
  for which you are an advisor).
    - The faculty will enter a response(accept/deny).
- Evaluate projects for which you are not an advisor.
    - Choose whether to approve the project or not.
      - If approved, change the status of the project from 'wait for evaluation' to 'Approve'.
      - If not approved, change the status of the project from 'wait for evaluation' to 'Processing'.
- See invitations to be an advisor for other projects (advisors can be advisors for more than one project).
    - Choose whether to accept or not.