<template>
  <VSearchBarButton
    id="content-settings-button"
    icon="source"
    :label="
      appliedFilterCount
        ? t('header.contentSettingsButton.withCount', {
            count: appliedFilterCount,
          })
        : t('header.contentSettingsButton.simple')
    "
    aria-haspopup="dialog"
    :aria-expanded="isPressed"
    aria-controls="content-settings-modal"
    variant="filled-white"
  >
    <template #notification>
      <span
        v-if="appliedFilterCount"
        class="absolute right-[-0.1875rem] top-[-0.1875rem] h-[0.5rem] w-[0.5rem] rounded bg-pink"
      />
    </template>
  </VSearchBarButton>
</template>
<script setup lang="ts">
import { useNuxtApp } from "#imports"

import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"

withDefaults(
  defineProps<{
    isPressed?: boolean
    appliedFilterCount?: number
  }>(),
  {
    isPressed: false,
    appliedFilterCount: 0,
  }
)
const {
  $i18n: { t },
} = useNuxtApp()
</script>
