<template>
  <VItem
    class="md:mb-1"
    :selected="selected"
    :is-first="itemId === 0"
    v-bind="component"
    @click.native="$emit('click', item)"
  >
    <div class="flex flex-row items-center text-base gap-2 py-2 w-full">
      <VIcon :icon-path="icon" />
      <span class="font-semibold">{{ $t(`search-type.${item}`) }}</span>
      <VPill v-if="status === 'beta'" class="ms-auto">{{
        $t('search-type.status-beta')
      }}</VPill>
    </div>
  </VItem>
</template>

<script>
import { computed, useContext, defineComponent } from '@nuxtjs/composition-api'

import { ALL_MEDIA, contentStatus } from '~/constants/media'
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

    const status = computed(() => {
      return contentStatus[props.item]
    })

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
      status,
    }
  },
})
</script>
