<template>
  <VSearchBarButton
    :icon-path="sourceIcon"
    :aria-label="
      areFiltersSelected
        ? $t('header.aria.menu-notification')
        : $t('header.aria.menu')
    "
    aria-haspopup="dialog"
    :aria-expanded="isPressed"
    aria-controls="content-settings-modal"
    inner-area-classes="bg-white hover:bg-dark-charcoal hover:text-white"
  >
    <template #notification>
      <span
        v-if="areFiltersSelected"
        class="absolute top-[-2px] right-[-2px] h-[8px] w-[8px] rounded bg-pink"
      />
    </template>
  </VSearchBarButton>
</template>
<script lang="ts">
import VSearchBarButton from '~/components/VHeader/VHeaderMobile/VSearchBarButton.vue'

import sourceIcon from '~/assets/icons/source.svg'

export default {
  name: 'VContentSettingsButton',
  components: { VSearchBarButton },
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
  setup() {
    return {
      sourceIcon: sourceIcon as unknown as string,
    }
  },
}
</script>
