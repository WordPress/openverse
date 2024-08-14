<script setup lang="ts">
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
</script>

<template>
  <VSearchBarButton
    id="content-settings-button"
    icon="source"
    :label="
      appliedFilterCount
        ? $t('header.contentSettingsButton.withCount', {
            count: appliedFilterCount,
          })
        : $t('header.contentSettingsButton.simple')
    "
    aria-haspopup="dialog"
    :aria-expanded="isPressed ? 'true' : 'false'"
    aria-controls="content-settings-modal"
    variant="filled-white"
  >
    <template #notification>
      <span
        v-if="appliedFilterCount"
        class="absolute right-[-0.1875rem] top-[-0.1875rem] h-[0.5rem] w-[0.5rem] rounded bg-primary"
      />
    </template>
  </VSearchBarButton>
</template>
