import icons from "~/assets/svg/sprite/icons.svg"
import images from "~/assets/svg/sprite/images.svg"
import licenses from "~/assets/svg/sprite/licenses.svg"

export const sprites = { icons, images, licenses }
export type Sprite = keyof typeof sprites

function isSprite(sprite: string): sprite is Sprite {
  return Object.keys(sprites).includes(sprite)
}

function generateName(name: string) {
  return name
    .toLowerCase()
    .replace(/\.svg$/, "")
    .replace(/[^a-z0-9-:]/g, "-")
    .replace(/:/g, "--")
}

export const useSprite = (name: string) => {
  let [sprite, icon] = name.split("/")

  if (!icon) {
    icon = sprite
    sprite = "icons"
  }
  if (!isSprite(sprite)) {
    throw new Error(`Sprite ${sprite} not found`)
  }

  /**
   * Find sprite file name after nuxt build
   */
  const spriteFile = sprites[sprite]

  return {
    sprite,
    icon,
    url: spriteFile + `#${generateName(icon)}`,
    class: `${sprite}`,
  }
}
