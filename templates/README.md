# Template workflow

Contributing to the linting templates can be unintuitive at first. If you follow
the process outlined below, it makes things a _lot_ easier to manage and
iterate.

## Process for editing jinja templates

1. Make changes to the jinja template
1. Run `just render-templates` to re-render all templates. This runs pretty
   quickly but if you need to go even faster, you can run the
   `render-precommit`, `render-prettier`, or `render-github` recipes instead to
   render only the specific files you're changing.
1. Confirm your rendered changes meet prettier's requirements by:
   1. Staging `.pre-commit-config.yaml` with `git add .pre-commit-config.yaml`
   1. Run `pre-commit run prettier`
   1. Run `git diff` to see any differences prettier may have made to the final
      output
   - This separate step is necessary because prettier does not lint the jinja
     files. For the rendered output of the jinja files to pass prettier, the
     templates themselves must be perfect, so you have to manually push changes
     that prettier will make into the templates. Often this is stuff like
     tedious whitespace, line-break, and indentation issues in the YAML or the
     Markdown templates.
1. If you had to make changes to appease prettier, follow steps 2 and 3 again
   and confirm there are no more changes from prettier.
1. You're done!
