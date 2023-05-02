<template>
  <VSearchBarButton
    id="content-settings-button"
    icon="source"
    :label="
      appliedFilterCount
        ? $tc('header.content-settings-button.with-count', appliedFilterCount)
        : $t('header.content-settings-button.simple')
    "
    aria-haspopup="dialog"
    :aria-expanded="isPressed"
    aria-controls="content-settings-modal"
    inner-area-classes="bg-white hover:bg-dark-charcoal hover:text-white"
    v-on="$listeners"
  >
    <template #notification>
      <span
        v-if="appliedFilterCount"
        class="absolute right-[-2px] top-[-2px] h-[8px] w-[8px] rounded bg-pink"
      />
    </template>
  </VSearchBarButton>
</template>
<script lang="ts">
import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"

export default {
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
}
</script>
