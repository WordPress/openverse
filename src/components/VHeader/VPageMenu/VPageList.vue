<template>
  <VItemGroup
    :direction="layout"
    class="mt-10 min-w-[200px] text-base md:mt-2"
    :bordered="false"
  >
    <VItem
      v-for="(page, idx) in pages.all"
      :key="page.id"
      class="w-1/2 md:w-full"
      :selected="page.id === pages.current.value"
      :is-first="idx === 0"
      v-bind="getLinkProps(page)"
      @click="$emit('click')"
    >
      <div class="flex flex-row">
        <span class="pe-2">{{ $t(page.name) }}</span>
        <VIcon
          v-if="isLinkExternal(page)"
          :icon-path="externalLinkIcon"
          :size="5"
          class="mb-0.5 self-center"
        />
      </div>
    </VItem>
  </VItemGroup>
</template>
<script lang="ts">
import { defineComponent, PropType } from '@nuxtjs/composition-api'

import usePages from '~/composables/use-pages'

import VIcon from '~/components/VIcon/VIcon.vue'
import VItem from '~/components/VItemGroup/VItem.vue'
import VItemGroup from '~/components/VItemGroup/VItemGroup.vue'

import externalLinkIcon from '~/assets/icons/external-link.svg'

export default defineComponent({
  name: 'VPageMenuPopover',
  components: { VIcon, VItem, VItemGroup },
  props: {
    layout: {
      type: String as PropType<'vertical' | 'columns'>,
      default: 'vertical',
    },
  },
  setup() {
    const pages = usePages()

    const isLinkExternal = (item) => !item.link.startsWith('/')
    const getLinkProps = (item) => ({ as: 'VLink', href: item.link })

    return {
      getLinkProps,
      isLinkExternal,
      externalLinkIcon,
      pages,
    }
  },
})
</script>
