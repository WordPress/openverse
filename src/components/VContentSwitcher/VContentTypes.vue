<template>
  <VItemGroup
    direction="vertical"
    :size="size"
    :bordered="bordered"
    :heading="$t('search-type.heading')"
    type="radiogroup"
    class="z-10"
  >
    <VContentItem
      v-for="(item, idx) in content.types"
      :key="item"
      :class="{ 'mb-1 p-4': size === 'medium' }"
      :item="item"
      :item-id="idx"
      :icon="content.icons[item]"
      :selected="item === activeItem"
      @click="handleClick(item)"
    />
  </VItemGroup>
</template>
<script>
import { supportedContentTypes } from '~/constants/media'
import useContentType from '~/composables/use-content-type'

import VItemGroup from '~/components/VItemGroup/VItemGroup.vue'
import VContentItem from '~/components/VContentSwitcher/VContentItem.vue'
import { computed, defineComponent } from '@nuxtjs/composition-api'

export default defineComponent({
  name: 'VContentTypes',
  components: { VItemGroup, VContentItem },
  props: {
    /**
     * 'Small' size for mobile screens,
     * 'medium' size for larger screens.
     */
    size: {
      type: String,
      default: 'small',
      validator: (val) => ['small', 'medium'].includes(val),
    },
    activeItem: {
      type: String,
      required: true,
      validator: (val) => supportedContentTypes.includes(val),
    },
  },
  setup(props, { emit }) {
    const content = useContentType()
    const bordered = computed(() => props.size === 'small')
    const handleClick = (item) => {
      emit('select', item)
    }
    return {
      content,
      bordered,
      handleClick,
    }
  },
})
</script>
