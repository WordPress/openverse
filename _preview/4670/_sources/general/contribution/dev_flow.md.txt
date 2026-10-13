# Development workflow

To contribute code to Openverse, follow the following steps.

1. Fork [the Openverse monorepo](https://github.com/WordPress/openverse). When
   you make a code change you will push the changes to a branch on your fork and
   make a PR to the original repo to incorporate those changes.

   Go to the repository page on GitHub and find the "Fork" button in the upper
   corner of the page. Click this and GitHub will guide you through the process
   of forking the repository.

1. Follow the guide in [general setup](/general/general_setup.md) to set up the
   `ov` development environment.

1. Refer to the quickstart guide of the part of the application for the issue
   you've chosen to work on.
   [They are linked in the general setup guide](/general/general_setup.md#up-and-running).

1. Work on the issue you've chosen. Check out a new branch from `main`, named
   after the issue you're solving. Create commits on this branch and push to
   your fork.

1. Once you have the solution, make a PR from your working branch on your fork
   to the `main` branch on the `origin` repo. You can make a PR even before you
   have a solution, but you should mark it as a draft. That PR will
   automatically update when you create new commits on your work branch.
