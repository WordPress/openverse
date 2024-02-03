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
        :label="closeButtonLabel || t('modal.closeBanner')"
        :class="{
          'focus-slim-tx-yellow hover:bg-white hover:bg-opacity-10':
            variant === 'dark',
        }"
        @click="$emit('close')"
      />
    </slot>
  </section>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import type { BannerId } from "~/types/banners"

import VIcon from "~/components/VIcon/VIcon.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

/**
 * Display a banner that can indicate one of four semantics in one of two color
 * variants.
 */
const props = withDefaults(
  defineProps<{
    /**
     * the semantic meaning of the banner; This can carry a positive, neutral
     * or negative connotation.
     */
    nature?: "info" | "warning" | "success" | "error"
    /**
     * the color variant of the banner; The dark variant is intended for use on
     * yellow pages.
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

defineEmits(["close"])
const {
  $i18n: { t },
} = useNuxtApp()

const classNames = computed(() =>
  props.variant === "dark"
    ? "bg-dark-charcoal text-white"
    : {
        info: "bg-info-soft",
        warning: "bg-warning-soft",
        success: "bg-success-soft",
        error: "bg-error-soft",
      }[props.nature]
)
const iconClassNames = computed(() =>
  props.variant === "dark"
    ? ""
    : {
        info: "text-info",
        warning: "text-warning",
        success: "text-success",
        error: "text-error",
      }[props.nature]
)
</script>
