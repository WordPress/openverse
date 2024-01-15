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
        class="absolute right-[-0.1875rem] top-[-0.1875rem] h-[0.5rem] w-[0.5rem] rounded bg-pink"
      />
    </template>
  </VSearchBarButton>
</template>
<script lang="ts">
import { defineComponent } from "vue"

import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"

export default defineComponent({
  name: "VContentSettingsButton",
  components: { VSearchBarButton },
  props: {
    isPressed: {
      type: Boolean,
      default: false,
    },
    appliedFilterCount: {
      type: Number,
      default: 0,
    },
  },
})
</script>
