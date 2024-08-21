<script setup lang="ts">
/**
 * Display a banner that can indicate one of four semantics in one of two color
 * variants.
 */
import { computed } from "vue"

import type { BannerId } from "~/types/banners"

import VIcon from "~/components/VIcon/VIcon.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

const props = withDefaults(
  defineProps<{
    /**
     * the semantic meaning of the banner; This can carry a positive, neutral
     * or negative connotation.
     */
    nature?: "info" | "warning" | "success" | "error"
    /**
     * the color variant of the banner; The dark variant is intended for use on
     * bg-complementary pages.
     */
    variant?: "regular" | "dark"
    /**
     * the unique ID of the banner
     */
    id: BannerId
    /**
     * the label to apply to the close button
     */
    closeButtonLabel?: string
  }>(),
  {
    nature: "info",
    variant: "regular",
  }
)

defineEmits<{
  close: []
}>()

const classNames = computed(() =>
  props.variant === "dark"
    ? "bg-tertiary text-over-dark"
    : {
        info: "bg-info",
        warning: "bg-warning",
        success: "bg-success",
        error: "bg-error",
      }[props.nature]
)
const iconClassNames = computed(() =>
  props.variant === "dark"
    ? ""
    : {
        info: "text-info-8",
        warning: "text-warning-8",
        success: "text-success-8",
        error: "text-error-8",
      }[props.nature]
)

const closeButtonClassNames = computed(() =>
  props.variant === "dark"
    ? "focus-slim-tx-bg-complementary hover:bg-tertiary-hover"
    : {
        info: "hover:!bg-info-3",
        warning: "hover:!bg-warning-3",
        success: "hover:!bg-success-3",
        error: "hover:!bg-error-3",
      }[props.nature]
)
</script>

<template>
  <section
    class="flex flex-row items-center gap-2 rounded-sm p-2 lg:p-3"
    :class="classNames"
    :data-testid="`banner-${id}`"
  >
    <slot name="start">
      <VIcon :name="nature" :class="iconClassNames" />
    </slot>

    <p class="caption-regular lg:paragraph-small flex-grow">
      <slot />
    </p>

    <slot name="end">
      <VIconButton
        :variant="variant === 'dark' ? 'transparent-tx' : 'transparent-gray'"
        :icon-props="{ name: 'close-small' }"
        size="small"
        :label="closeButtonLabel || $t('modal.closeBanner')"
        :class="closeButtonClassNames"
        @click="$emit('close')"
      />
    </slot>
  </section>
</template>
