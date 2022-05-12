<template>
  <VButton
    v-show="canLoadMore"
    size="large"
    variant="full"
    :disabled="isFetching"
    data-testid="load-more"
    @click="onLoadMore"
  >
    {{ buttonLabel }}
  </VButton>
</template>
<script lang="ts">
import { computed, defineComponent } from '@nuxtjs/composition-api'

import { useMediaStore } from '~/stores/media'
import { useSearchStore } from '~/stores/search'
import { useI18n } from '~/composables/use-i18n'

import VButton from '~/components/VButton.vue'

export default defineComponent({
  name: 'VLoadMore',
  components: {
    VButton,
  },
  setup() {
    const i18n = useI18n()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const canLoadMore = computed(
      () =>
        searchStore.searchTerm !== '' &&
        mediaStore.fetchState.canFetch &&
        mediaStore.resultCount > 0
    )
    const onLoadMore = async () => {
      if (!canLoadMore.value) return

      await mediaStore.fetchMedia({
        shouldPersistMedia: true,
      })
    }
    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const buttonLabel = computed(() => i18n.t('browse-page.load'))

    return {
      buttonLabel,
      isFetching,
      onLoadMore,
      canLoadMore,
    }
  },
})
</script>
