<script setup lang="ts">
/**
 * The icon-only version of VButton component. In some cases, VButton is replaced
 * with VIconButton in small breakpoints.
 */
import { computed } from "vue"

import type {
  ButtonConnections,
  ButtonSize,
  ButtonVariant,
} from "~/types/button"

import VIcon, { type IconProps } from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

const props = defineProps<{
  /**
   * The size of the button, matches the sizes of VButton component.
   */
  size: ButtonSize
  /**
   * The visual variant of the button, matches the variants of VButton component.
   */
  variant: ButtonVariant
  /**
   * Props to pass down to the `VIcon` component nested inside the button.
   * See documentation on `VIcon`.
   */
  iconProps?: IconProps
  /**
   * Connections to pass down to the `VButton` component nested inside the button.
   */
  connections?: ButtonConnections[]
  /**
   * The label used for accessibility purposes.
   */
  label: string
}>()

const iconSize = computed(() => props.iconProps?.size ?? 6)
</script>

<template>
  <VButton
    :aria-label="label"
    :size="size"
    :variant="variant"
    :connections="connections"
    class="icon-button"
    icon-only
  >
    <slot name="default" :icon-size="iconSize" />
    <VIcon
      v-if="iconProps"
      class="pointer-events-none"
      :size="iconSize"
      v-bind="iconProps"
    />
  </VButton>
</template>
