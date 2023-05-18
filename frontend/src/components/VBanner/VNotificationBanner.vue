<template>
  <section
    class="flex flex-row items-start gap-2 rounded-sm px-2 py-3 lg:p-4"
    :class="classNames"
    :data-testid="`banner-${id}`"
  >
    <slot name="start">
      <VIcon :name="icon" :class="iconClassNames" />
    </slot>

    <p class="caption-regular lg:paragraph-small flex-grow">
      <slot />
    </p>

    <slot name="end">
      <VCloseButton
        class="flex-grow-0"
        variant="plain--avoid"
        size="tiny"
        icon-size="medium"
        :label="closeButtonLabel || $t('modal.close-banner')"
        @close="$emit('close')"
      />
    </slot>
  </section>
</template>

<script lang="ts">
import { defineComponent, PropType, computed } from "vue"

import { defineEvent } from "~/types/emits"

import type { BannerId } from "~/types/banners"

import VIcon from "~/components/VIcon/VIcon.vue"
import VCloseButton from "~/components/VCloseButton.vue"

import type { TranslateResult } from "vue-i18n"

/**
 * Display a banner that can indicate one of four semantics in one of two color
 * variants.
 */
export default defineComponent({
  name: "VNotificationBanner",
  components: {
    VIcon,
    VCloseButton,
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
     * yellow pages.
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
        ? "bg-dark-charcoal text-white"
        : {
            info: "bg-info-light",
            warning: "bg-warning-light",
            success: "bg-success-light",
            error: "bg-error-light",
          }[props.nature]
    )

    const icon = computed(() =>
      props.nature === "success" ? "check" : props.nature
    )
    const iconClassNames = computed(() =>
      props.variant === "dark"
        ? ""
        : {
            info: "text-info-dark",
            warning: "text-warning-dark",
            success: "text-success-dark",
            error: "text-error-dark",
          }[props.nature]
    )

    return {
      classNames,
      icon,
      iconClassNames,
    }
  },
})
</script>
