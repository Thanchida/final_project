## **TO EVALUATE**
- Lead submitted project.
  - Conditions for a lead who needs to submit a project:
      - The lead must have a full complement of members and advisors, as required.
      - The project has to be modified.
- Advisor needs to request two evaluators to assess the project.
- Evaluators evaluate the project.
  - Both evaluators must approve the project for the status to change to 'Approved.'
  - If one of the evaluators denies the project, the project status will be 'Under review.'

## **OUTLINE CODE TO PERFORM**
- **The 'evaluation' method**
  - Retrieves information about available projects for evaluation.
  - Takes user input for the project ID they want to evaluate.
  - Checks if the user is assigned as an evaluator for the selected project.
  - Asks the evaluator for approval or denial and updates the evaluation status accordingly.
  - Return project ID

- **The 'approve_project' method**
  - Calls the 'evaluation' method to get the project ID for evaluation.
  - Checks if there's a project available for evaluation.
  - Retrieves project and evaluation data from the database.
  - Checks if the project has been evaluated by both evaluators.
  - Calculates the total number of approvals from both evaluators.
  - Updates the project status based on the number of approvals

The 'evaluation' method and 'approve_project' method will be in the 'Faculty' class and the 'Advisor' class. If a faculty
member accepts an invitation to be an advisor for a project, their role will change to 'advisor.' Therefore, I will implement
the 'evaluation' and 'approve_project' methods in the 'Advisor' class as well, allowing them to evaluate other projects in addition 
to their own