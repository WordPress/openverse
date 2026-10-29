# Miscellaneous notes on the frontend

## Formatting and Linting

The code in this repository is formatted using `prettier`. If you have prettier
setup in your code editor it should work out of the box; otherwise you can use
the `./ov just frontend/run lint` script to format and fix lint errors in your
code. Checks are run to lint your code and validate the formatting on git
precommit.

You will need to fix any linting issues before committing. We recommend
formatting your JavaScript files on save in your text editor. You can learn how
to do this in Visual Studio Code
[here](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode#format-on-save).

### File name conventions

All files and folders should be written in `kebab-case`, with the exception of
Vue single file components. If it ends in `.vue`, please use `PascalCase`. This
distinction makes our component files stand out clearly and is
[recommended by the Vue community](https://vuejs.org/v2/style-guide/#Single-file-component-filename-casing-strongly-recommended).

## Redirects <a name = "redirects"></a>

| From         | To          | Status code | Setup level            |
| ------------ | ----------- | ----------- | ---------------------- |
| /photos/\_id | /image/\_id | 301         | Nuxt server middleware |

## Frontend Components

The frontend app is composed of a number of components that are documented in
our [Storybook](https://docs.openverse.org/storybook/).

### How to create a component

To create a component you can run:

```shell
# Make sure you have run `pnpm install` at least once before.
pnpm run create:component [component name in PascalCase]
for example: pnpm run create:component VButtonGreen
```

This command will create a component file, a story file for the component, a
unit test file, and a regression test file. It also adds the component name to
tsconfig.ts `include` property. Each file will have a basic template to start
working with. We use the
[itsjonq/remake](https://www.npmjs.com/package/@itsjonq/remake?activeTab=readme)
package to create files out of templates.

You can also create all those files manually by running the following commands:

<b>create a component file </b>

```
pnpm run create:component-sfc --output=[path] --name=[component name]
```

<b>create a story file </b>

```
pnpm run create:story --output=[path] --name=[component name]
```

<b>create a component unit test file</b>

```
pnpm run create:component-unit-test --output=[path] --name=[component name] --fileName=[component name in kebab-case]
```

<b>create a component regression test file</b>

```
pnpm run create:component-storybook-test --output=[path] --name=[component name kebab-case] --fileName=[component name in kebab-case]
```

### CSS Framework

To design our components, we use the [TailwindCSS](https://tailwindcss.com/)
utility-first CSS framework. We have compiled a list of TailwindCSS classes that
are used in the frontend app. You can view the list
[here](https://docs.openverse.org/tailwind/).

### Development Tips

If you use VS Code, you can install the
[Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)
extension to get autocomplete for TailwindCSS classes.

## Finding your local IP address

You can find the local IP address Nuxt uses by looking at the output of
`nuxt dev`. Look in your console for a box of configuration details that looks
like this:

```bash
#  ╭───────────────────────────────────────────╮
#  │                                           │
#  │   Nuxt @ v2.15.8                          │
#  │                                           │
#  │   ▸ Environment: development              │
#  │   ▸ Rendering:   server-side              │
#  │   ▸ Target:      server                   │
#  │                                           │
#  │   Listening: http://192.168.50.119:8443/  │ # <-- Use this IP Address
#  │                                           │
#  ╰───────────────────────────────────────────╯
```

You will need to regenerate the certificate if this IP address changes for any
reason, like by enabling a VPN or changing networks.
