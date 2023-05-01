# SVG Icon Sprites in Openverse Frontend

We use SVG for icons in Openverse frontend because it allows for high-quality
graphics, easy scalability without losing quality, and small file sizes. To
reduce the number of HTTP requests for icons and reduce load times, we combine
all of them into a single file called SVG sprite. An SVG sprite is a single SVG
file that contains multiple SVG symbols. Each symbol can be accessed using its
unique ID.

This guide explains how to use SVG sprites in Openverse Frontend and how to add
a new SVG file to the sprite.

## Using SVG Sprites in Openverse Frontend

You can use SVG sprites through the `VIcon` component. To use it, first, import
it into your component:

```js
import { VIcon } from "~/components/VIcon"
```

Then, add the VIcon component to your template, passing the name of the icon as
a prop:

```html
<template>
  <VIcon name="arrow-up" />
</template>
```

The name prop is used to identify the icon within the SVG sprite. You can find
the names of the available icons in the `frontend/src/assets/icons/sprites.json`
file. The default icons listed in the object with the name `icons` use the name
as is, without prefixes. To use the license icons, you would need to add
`license/` as a prefix to the name. For example, to use an `external-link` icon,
you would use the name `external-link`, and for the `cc-by` icon, you would use
the name `license/cc-by`.

You can also view a list of all available icons if you go to
`http://localhost:8443/_icons`. You can copy the icon name (with the prefix, if
necessary) by clicking on the icon. This page is only available in development
environment and is not available in production.

## Adding New Icons to the Sprite

Openverse uses
[svg-sprite-module](https://github.com/nuxt-community/svg-sprite-module) to
automatically generate the SVG sprite when you add an SVG file to
`frontned/src/assets/icons/raw/`. It runs when you run `just frontend/run dev`
or `just frontend/run build`. The module also watches the content of the
`frontend/src/assets/icons/raw` directory, and re-generates the sprite if you
add an icon there, so you don't need to re-run the app.

So, to add a new icon to the SVG sprite, you only need to create an SVG file
containing the icon in `frontend/src/assets/icons/raw/` directory. The name of
the file without the `.svg` extension will be used in the component. There are
several requirements for the file:

- It should contain the SVG code for the icon, with a `path` with `id` icon that
  wraps the inner contents.
- The color of the icon should be `currentColor`. This allows the icon to
  inherit the color of the parent element. Also, remove white backgrounds from
  the icon.
- It should have a `viewBox` attribute with the dimensions of the icon.
  Openverse uses 24x24 icons. If you are exporting the icon from Figma, resize
  the containing frame to 24x24 before exporting.
