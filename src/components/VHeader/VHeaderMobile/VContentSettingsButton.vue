<template>
  <span class="relative inline-block h-8 w-8">
    <VIconButton
      size="new-small"
      :icon-props="{ iconPath: sourceIcon }"
      :button-props="{ variant: 'menu' }"
      :aria-label="
        areFiltersSelected
          ? $t('header.aria.menu-notification')
          : $t('header.aria.menu')
      "
      aria-haspopup="dialog"
      :aria-expanded="isPressed"
      aria-controls="content-settings-modal"
      @click="$emit('click')"
    />
    <span
      v-if="areFiltersSelected"
      class="absolute top-[-2px] right-[-2px] h-[8px] w-[8px] rounded bg-pink"
    />
  </span>
</template>

<script lang="ts">
import { defineEvent } from '~/types/emits'

import VIconButton from '~/components/VIconButton/VIconButton.vue'

import sourceIcon from '~/assets/icons/source.svg'

export default {
  name: 'VContentSettingsButton',
  components: { VIconButton },
  props: {
    isPressed: {
      type: Boolean,
      default: false,
    },
    areFiltersSelected: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    click: defineEvent(),
  },
  setup() {
    return {
      sourceIcon,
    }
  },
}
</script>
