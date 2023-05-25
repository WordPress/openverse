<template>
  <section
    class="flex flex-row items-center gap-2 rounded-sm p-2 lg:px-3 lg:py-4"
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
      <VCloseButton
        class="flex-grow-0"
        variant="transparent-gray"
        size="tiny"
        icon-size="small"
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

    return {
      classNames,
      iconClassNames,
    }
  },
})
</script>
