# Arborist is a testbed for software dev automations

## Core idea
Simply call the launch script with the name of the project you want to
arborist to work on.

```./run_arborist.sh <folder>```

## Setting up a new project.

1. Create a new folder in the project (If this is managed in git independently add it to the .gitignore)
2. Add a file to the new project called SEED.md described below.
3. Run `run_arborist.sh` on the file!

## Using Arborist

- As much as possible, only change `SEED.md` and be as high level as possible 
while achieving the behaviour you want.
- If you notice a bad behaviour, try to figure out why that happened and update 
the arborist project to improve future projects.
- If you have specific feedback about how something is working, add it to `feedback.md`

## SEED.md

The seed file should outline what you want the project to be.

1. Start with the highest level, most abstract description of the project.
2. Add any more details you need to steer the output below.
3. This is a living document, change it at any time!

Here's an example:

I want a user-friendly command line tool that will play any classic boardgame against the user.

It should have a single script that has a nice menu to select the game. The user should 
have a limited but useful set of UI navigation tools. For now, start with the 3 most popular 
classic boardgames.
