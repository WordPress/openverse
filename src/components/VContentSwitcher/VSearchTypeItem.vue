<template>
  <VItem
    :selected="selected"
    :is-first="itemId === 0"
    v-bind="component"
    @click.native="$emit('click', item)"
  >
    <div class="flex flex-row items-center text-base">
      <VIcon :icon-path="icon" class="me-2 my-2" />
      <span class="pe-20 font-semibold">{{ $t(`search-type.${item}`) }}</span>
      <VPill v-if="status === 'beta'">{{
        $t('search-type.status-beta')
      }}</VPill>
    </div>
  </VItem>
</template>

<script>
import { computed, useContext, useRoute } from '@nuxtjs/composition-api'
import { defineComponent } from '@vue/composition-api'

import { ALL_MEDIA, contentStatus } from '~/constants/media'

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
    const route = useRoute()

    const status = computed(() => {
      return contentStatus[props.item]
    })

    /**
     * The query is temporarily set to the incorrect value here: it uses the existing query
     * that is set for selected search type. When the search store conversion PR is merged,
     * we will set the query specific for the search type using `computeQueryParams(props.item)` method.
     */
    const component = computed(() => {
      if (!props.useLinks) {
        return {}
      }
      return {
        as: 'VLink',
        href: app.localePath({
          path: `/search/${props.item === ALL_MEDIA ? '' : props.item}`,
          // query: searchStore.computeQueryParams(props.item),
          query: route.value.query,
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
