# Main README file

## Git documentation
This is a test change to show how the following git commands work:

- git status - shows which files were changed. it doesn't show the actual changes
- git diff - shows the actual changes per file
- git add <filename> or git add . - adds the filenames or all the files in the folder (and sub-folders) to the commit
- git commit - opens a terminal window to write a commit message. Commit message consists of the title (first line), empty line, and description (any number of lines of text). To start typing the commit message you need to press "i". to stop typing the commit message, you need to press "esc". to exit with saving you need to press ":wq" (stands for quit-write). to exit without saving you need to press ":q!" (stands for force-quit)
- git pull --rebase origin main && git push origin main:feruza/first_commit - pulls the latest changes from main, creates a new branch out of main, and pushes the changes to the branch called "feruza/first_commit". You can put any name after main:. main: means create a new branch as a copy of the main branch. As a result, this command will print a url to create a pull request. You can copy that url, open it in browser, and create a pull request. Pull request means that once approved changes from "feruza/first_commit" branch will be merged to the main branch. Once done, if anyone else types the command "git pull --rebase origin main", they will get your changes as well.

If you made a mistake, then you can reset your commit with "git reset HEAD~1" command. It means that it's resetting one commit without deleting the changes.
If you want to also delete the changes, then you need to use "git reset --hard HEAD~1" command.

Before making a change, you always need to start with pulling the latest changes from remote repository.
E.g. if you had a pull request that got merged, then you won't get the main with latest changes unless you pull the latest changes.

First, you need to check the status with "git status" command.
If you already had uncommitted changes, then you need to run "git stash" command. It saves the changes in buffer and cleans the local repo.
Then you need to run "git status" again. If the result says "your local is ahead of remote by 1 commit", then most probably it's because of pushing your changes to a new branch in a single command.
First you need to delete that commit. Don't worry, you already pushed it to remote and merged with your pull request.
To delete your local commit you need to run "git reset --hard HEAD~1". It tells the git to hard-delete 1 commit.
Then check again with "git status". If it doesn't say anything about difference in number of commits, then you are good to go.

Then pull the latest changes with "git pull --rebase origin main" command.
Then restore your stashed changes with "git stash pop".


## Project documentation

backend / models
- input_output_models.py - stores the input and output types

Currently it has 3 classes:
- RecommendationRequest - input type to get recommendations
- FoodSuggestion - output type to return food suggestions
- FullRecommendationResponse - output type for the recommendation request API

Also created a requirements.txt file to start building up the environment.
Currently added "pydantic" requirement which has the "BaseModel" superclass which reduces the need for boilerplate code to define simple classes without having to specify getters and setters for the fields of the classes.
More details in [this doc](https://docs.pydantic.dev/latest/api/base_model/)
