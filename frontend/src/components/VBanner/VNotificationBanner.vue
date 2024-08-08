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

<script lang="ts">
import { defineComponent, PropType, computed } from "vue"

import { defineEvent } from "~/types/emits"

import type { BannerId } from "~/types/banners"

import VIcon from "~/components/VIcon/VIcon.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

import type { TranslateResult } from "vue-i18n"

/**
 * Display a banner that can indicate one of four semantics in one of two color
 * variants.
 */
export default defineComponent({
  name: "VNotificationBanner",
  components: {
    VIconButton,
    VIcon,
  },
  props: {
    /**
     * the semantic meaning of the banner; This can carry a positive, neutral
     * or negative connotation.
     */
    nature: {
      type: String as PropType<"info" | "warning" | "success" | "error">,
      default: "info",
    },
    /**
     * the color variant of the banner; The dark variant is intended for use on
     * bg-fill-complementary pages.
     */
    variant: {
      type: String as PropType<"regular" | "dark">,
      default: "regular",
    },
    /**
     * the unique ID of the banner
     */
    id: {
      type: String as PropType<BannerId>,
      required: true,
    },
    /**
     * the label to apply to the close button
     */
    closeButtonLabel: {
      type: [String, Object] as PropType<string | TranslateResult>,
    },
  },
  emits: {
    close: defineEvent(),
  },
  setup(props) {
    const classNames = computed(() =>
      props.variant === "dark"
        ? "bg-fill-tertiary text-over-dark"
        : {
            info: "bg-fill-info",
            warning: "bg-fill-warning",
            success: "bg-fill-success",
            error: "bg-fill-error",
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
        ? "focus-slim-tx-bg-fill-complementary hover:bg-fill-tertiary-hover"
        : {
            info: "hover:!bg-info-3",
            warning: "hover:!bg-warning-3",
            success: "hover:!bg-success-3",
            error: "hover:!bg-error-3",
          }[props.nature]
    )

    return {
      classNames,
      iconClassNames,
      closeButtonClassNames,
    }
  },
})
</script>
