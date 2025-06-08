# Main README file

This is a test change to show how the following git commands work:

- git status - shows which files were changed. it doesn't show the actual changes
- git diff - shows the actual changes per file
- git add <filename> or git add . - adds the filenames or all the files in the folder (and sub-folders) to the commit
- git commit - opens a terminal window to write a commit message. Commit message consists of the title (first line), empty line, and description (any number of lines of text). To start typing the commit message you need to press "i". to stop typing the commit message, you need to press "esc". to exit with saving you need to press ":wq" (stands for quit-write). to exit without saving you need to press ":q!" (stands for force-quit)
- git pull --rebase origin main && git push origin main:feruza/first_commit - pulls the latest changes from main, creates a new branch out of main, and pushes the changes to the branch called "feruza/first_commit". You can put any name after main:. main: means create a new branch as a copy of the main branch. As a result, this command will print a url to create a pull request. You can copy that url, open it in browser, and create a pull request. Pull request means that once approved changes from "feruza/first_commit" branch will be merged to the main branch. Once done, if anyone else types the command "git pull --rebase origin main", they will get your changes as well.

If you made a mistake, then you can reset your commit with "git reset HEAD~1" command. It means that it's resetting one commit without deleting the changes.
If you want to also delete the changes, then you need to use "git reset --hard HEAD~1" command.
