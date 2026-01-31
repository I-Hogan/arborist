# Steps for completing the next `todo.md` item

1. Complete any tasks already in tasks.md.
2. Check the code to see if the top item in `todo.md` has been completed.
3. If not, plan out the tasks required to complete the item (see bellow) 
and add them to `tasks.md`.
4. Complete all the tasks in tasks.md.

## Tasks required to complete a work item

Add the tasks to `tasks.md` then complete them one at a time, removing a task 
only after you are confident it is complete.

1. If necessary, research topics related to the work item and update `research/`.
2. Come up with a plan that follows `best_practices.md`.
3. Implement the change.
4. Run `scripts/pre-commit.sh`.
5. Review the change referencing `code_review.md`. Fix any issues you find. 
Run `scripts/pre-commit.sh` again if there are any changes.
6. For this task, come up with a definition of done (DoD), the last task should 
be checking whether the change meets the DoD, and if it meets the definition, 
do the following:
- Add an entry to `work_log.md` for the item. 
- Remove the item from the todo list.

