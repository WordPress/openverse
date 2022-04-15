<template>
  <ul
    class="meta-sources flex flex-col md:flex-row flex-wrap items-stretch gap-4 w-full"
  >
    <li v-for="source in sources" :key="source.name">
      <VButton
        as="VLink"
        variant="tertiary"
        size="disabled"
        :href="source.url"
        class="w-full md:w-auto text-sr font-bold p-4 md:py-2 md:px-3"
      >
        {{ source.name }}
        <sup class="top-0">
          <VIcon
            :icon-path="icons.externalLink"
            :size="4"
            :rtl-flip="true"
            class="ms-2"
          />
        </sup>
      </VButton>
    </li>
  </ul>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { getAdditionalSources } from '~/utils/get-additional-sources'
import type { ApiQueryParams } from '~/utils/search-query-transform'
import type { MediaType } from '~/constants/media'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'

import externalLinkIcon from '~/assets/icons/external-link.svg'

/**
 * This component renders a list of pre-populated links to additional sources
 * when there are insufficient or zero search results.
 */
export default defineComponent({
  name: 'VMetaSourceList',
  components: { VButton, VIcon },
  props: {
    /**
     * the media type to use as the criteria for filtering additional sources
     */
    type: { type: String as PropType<MediaType>, required: true },
    /**
     * the search query to pre-populate in the additional sources link
     */
    query: { type: Object as PropType<ApiQueryParams>, required: true },
  },
  setup(props) {
    const sources = computed(() =>
      getAdditionalSources(props.type, props.query)
    )

    return {
      icons: {
        externalLink: externalLinkIcon,
      },
      sources,
    }
  },
})
</script>
