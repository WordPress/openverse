#!/bin/bash
# $1 = the first argument in the command line

if [ -z "$1" ]; then
  echo "Please enter a component name"
  exit 1
else
  # transforms component name from PascalCase to kebab-case
  componentNameInKebabCase=$(echo "$1" | sed 's/\(.\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')

  pnpm run create:component-scaffolding "$1" "$componentNameInKebabCase"

  echo "Completed"
fi
