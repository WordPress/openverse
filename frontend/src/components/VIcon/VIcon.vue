<template>
  <svg
    :viewBox="viewBox"
    focusable="false"
    class="v-icon flex-none"
    :class="[`w-${size}`, `h-${size}`, { 'rtl-flip': rtlFlip }, icon.class]"
    aria-hidden="true"
  >
    <use :href="icon.url" />
  </svg>
</template>

<script lang="ts" setup>
import { ref, watch } from "vue"

import { useSprite } from "~/composables/use-sprite"
/**
 * Displays the given icon in a 24px × 24px square.
 */
export type IconProps = {
  name: string
  viewBox?: string
  gId?: string
  size?: number
  rtlFlip?: boolean
}
const props = withDefaults(
  defineProps<{
    /**
     * the path to the icon SVG; In a bundled application like Openverse,
     * importing an SVG should give us the path to the file.
     */
    name: string
    viewBox?: string
    /**
     * the ID of the `g` element to import from the icon; This element should
     * ideally have the `id` as "icon" and the `fill` as `currentColor`.
     */
    gId?: string
    /**
     * The size of the icon based on tailwind values. Possible values:
     * 4 - 1rem, 5 - 1.25rem, 6 - 1.5rem, 8 - 2rem, 10 - 2.5rem,  12 - 3rem.
     *
     * @default 6
     */
    size?: number
    /**
     * whether to flip the icon for RTL languages; This generally makes sense
     * for directional icons such as those involving arrows.
     */
    rtlFlip?: boolean
  }>(),
  {
    viewBox: "0 0 24 24",
    gId: "icon",
    size: 6,
    rtlFlip: false,
  }
)

if (!props.viewBox.split(" ").every((v) => !isNaN(parseInt(v)))) {
  throw new Error(
    `Invalid viewBox "${props.viewBox}" for icon "${props.name}".`
  )
}
if (![4, 5, 6, 8, 10, 12].includes(props.size)) {
  throw new Error(`Invalid size "${props.size}" for icon "${props.name}".`)
}

const icon = ref({
  url: "",
  class: "",
})

icon.value = useSprite(
  props.name.includes("/") ? props.name : `icons/${props.name}`
)

watch(
  () => props.name,
  (name) => {
    icon.value = useSprite(name)
  }
)
</script>

<style scoped>
[dir="rtl"] .v-icon.rtl-flip {
  @apply -scale-x-100 transform;
}
</style>
