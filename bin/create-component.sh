#!/bin/bash
# $1 = the first argument in the command line

if [ -z "$1" ]
  then
    echo "Please enter a component name"
    exit 1;
  else
    # transforms component name from PascalCase to kebab-case
    componentNameInKebabCase=$(echo "$1" | sed 's/\(.\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')

    pnpm run create:component-scaffolding "$1" "$componentNameInKebabCase"

    # comment-json package changes the code style of tsconfig.json.
    # if you try to commit your newly created component,
    # it will fail the first time because it won`t pass prettier checks.
    # to avoid this, we are runing prettier at the end of the component creation proccess.
    echo "runing Prettier on tsconfig.json..."
    pnpm prettier --write tsconfig.json
    echo "Completed"
fi
