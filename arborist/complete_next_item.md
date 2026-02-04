# Steps for completing the next `arborist/todo.md` item

1. Check if there is any user feedback in `arborist/feedback.md`. If there is, decide whether 
it makes sense to add either a todo work item(s) (or a task if it is a small request) 
in response. Add new items to the bottom of the list. Once done, remove the feedback 
from the `arborist/feedback.md` file. Items in todo will be broken into work tasks by the agent, 
only specify high level objectives (unless specifics were provided in the feedback). 
Depending on the feedback, you may need to update `SEED.md`.
2. Complete any tasks already in arborist/tasks.md.
3. Check the code to see if the top item in `arborist/todo.md` has been completed.
4. If not, plan out the tasks required to complete the item (see bellow) 
and add them to `arborist/tasks.md`.
5. Complete all the tasks in arborist/tasks.md.

## Tasks required to complete a work item

Add the tasks to `arborist/tasks.md` then complete them one at a time, removing a task 
only after you are confident it is complete.

1. If necessary, research topics related to the work item and update `research/`.
2. Come up with a plan that follows `best_practices.md`.
3. Implement the change.
4. Run `scripts/pre_commit.sh`.
5. Review the change referencing `code_review.md`. Fix any issues you find. 
Run `scripts/pre_commit.sh` again if there are any changes.
6. For this task, come up with a definition of done (DoD) and write a 
check against that as the task (don't say writing a DoD is part of the task). 
The last task should be checking whether the change meets the DoD, and if it 
meets the definition, do the following:
- Add an entry to `arborist/work_log.md` for the item. 
- Remove the item from the todo list.
