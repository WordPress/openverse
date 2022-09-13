<template>
  <VItem
    class="md:mb-1"
    :selected="selected"
    :is-first="itemId === 0"
    v-bind="component"
    @click.native="$emit('click', item)"
  >
    <div class="flex w-full flex-row items-center gap-2 py-2 text-base">
      <VIcon :icon-path="icon" />
      <span class="font-semibold">{{ $t(`search-type.${item}`) }}</span>
      <VPill v-if="isBeta" class="ms-auto">{{
        $t('search-type.status-beta')
      }}</VPill>
    </div>
  </VItem>
</template>

<script>
import { computed, useContext, defineComponent } from '@nuxtjs/composition-api'

import { ALL_MEDIA, BETA, contentStatus } from '~/constants/media'
import { useSearchStore } from '~/stores/search'

import VIcon from '~/components/VIcon/VIcon.vue'
import VItem from '~/components/VItemGroup/VItem.vue'
import VPill from '~/components/VPill.vue'

/** @typedef {import('@nuxtjs/composition-api').ExtractPropTypes<typeof propTypes>} Props */
const propTypes = {
  item: { type: String, required: true },
  itemId: { type: Number, required: true },
  selected: { type: Boolean, default: false },
  icon: { type: String, required: true },
  useLinks: { type: Boolean, default: true },
}
export default defineComponent({
  name: 'VSearchTypeItem',
  components: { VIcon, VItem, VPill },
  props: propTypes,
  setup(props) {
    const { app } = useContext()
    const searchStore = useSearchStore()

    const isBeta = computed(() => contentStatus[props.item] === BETA)

    /**
     * The query sets the filters that are applicable for the specific search type.
     */
    const component = computed(() => {
      if (!props.useLinks) {
        return {}
      }
      return {
        as: 'VLink',
        href: app.localePath({
          path: `/search/${props.item === ALL_MEDIA ? '' : props.item}`,
          query: searchStore.computeQueryParams(props.item),
        }),
      }
    })
    return {
      component,
      isBeta,
    }
  },
})
</script>
