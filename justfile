set dotenv-load := false

# Show all available recipes
default:
    pnpm run

# Run a package.json script via pnpm
run *args:
    pnpm run {{ args }}
