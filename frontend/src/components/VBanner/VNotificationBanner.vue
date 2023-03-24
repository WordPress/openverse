<template>
  <section
    class="flex items-center justify-between gap-x-2 px-4 py-2 md:px-7"
    :class="$style[variant]"
    :data-testid="`banner-${id}`"
  >
    <p class="caption-regular md:description-regular text-left">
      <slot name="default" />
    </p>
    <slot name="buttons">
      <VCloseButton
        variant="filled-transparent"
        icon-size="large"
        :label="closeButtonLabel || $t('modal.close-banner').toString()"
        @close="$emit('close')"
      />
    </slot>
  </section>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import { defineEvent } from "~/types/emits"

import type { BannerId } from "~/types/banners"

import VCloseButton from "~/components/VCloseButton.vue"

export default defineComponent({
  name: "VNotificationBanner",
  components: {
    VCloseButton,
  },
  props: {
    variant: {
      type: String as PropType<"announcement" | "informational">,
      required: true,
    },
    id: {
      type: String as PropType<BannerId>,
      required: true,
    },
    closeButtonLabel: {
      type: String,
    },
  },
  emits: {
    close: defineEvent(),
  },
})
</script>

<style module>
/* Styles from learn.wordpress.org */
.informational {
  background-color: #fff8e5;
  border-left: 0.25rem solid #ffb900;
}

.announcement {
  @apply bg-trans-blue text-white;
  border-left: 0.25rem solid transparent;
}
</style>
