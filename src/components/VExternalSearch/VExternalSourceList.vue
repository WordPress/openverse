<template>
  <VPopover
    ref="sourceListPopover"
    class="flex items-stretch"
    :label="$t('external-sources.button').toString()"
    placement="top-start"
  >
    <template #trigger="{ a11yProps }">
      <VButton
        :pressed="a11yProps['aria-expanded']"
        :aria-haspopup="a11yProps['aria-haspopup']"
        aria-controls="source-list-popover"
        variant="action-menu-bordered"
        size="disabled"
        class="caption-regular justify-between py-1 px-3 text-dark-charcoal pe-2"
        >{{ $t('external-sources.button').toString() }}
        <VIcon
          class="text-dark-charcoal-40 ms-1"
          :class="a11yProps['aria-expanded'] ? 'rotate-180' : 'rotate-0'"
          :icon-path="icons.caretDown"
      /></VButton>
    </template>
    <template #default="{ close }">
      <div
        class="relative max-w-[280px] p-2 pt-0"
        data-testid="source-list-popover"
      >
        <VIconButton
          class="absolute top-0 border-none text-dark-charcoal-70 end-0"
          size="search-medium"
          :icon-props="{ iconPath: icons.closeSmall }"
          :button-props="{
            'aria-label': $t('modal.close').toString(),
            variant: 'plain',
          }"
          @click="close"
        />
        <h2 class="description-bold mb-2 px-4 pt-5 text-start">
          {{ $t('external-sources.title') }}
        </h2>
        <p class="caption-regular mb-4 px-4 text-start">
          {{ $t('external-sources.caption', { openverse: 'Openverse' }) }}
        </p>
        <VButton
          v-for="source in sources"
          :key="source.name"
          as="VLink"
          variant="plain"
          size="disabled"
          class="caption-bold w-full justify-between px-4 py-3 text-dark-charcoal hover:bg-dark-charcoal-10"
          :href="source.url"
        >
          {{ source.name }}
          <VIcon
            :icon-path="icons.externalLink"
            :size="4"
            :rtl-flip="true"
            class="ms-2"
          />
        </VButton>
      </div>
    </template>
  </VPopover>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { getAdditionalSources } from '~/utils/get-additional-sources'
import type { ApiQueryParams } from '~/utils/search-query-transform'
import type { MediaType } from '~/constants/media'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VIconButton from '~/components/VIconButton/VIconButton.vue'
import VPopover from '~/components/VPopover/VPopover.vue'

import externalLinkIcon from '~/assets/icons/external-link.svg'
import caretDownIcon from '~/assets/icons/caret-down.svg'
import closeSmallIcon from '~/assets/icons/close-small.svg'

/**
 * This component renders a list of pre-populated links to additional sources
 * when there are insufficient or zero search results.
 */
export default defineComponent({
  name: 'VExternalSourceList',
  components: { VButton, VIcon, VIconButton, VPopover },
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
        caretDown: caretDownIcon,
        closeSmall: closeSmallIcon,
      },
      sources,
    }
  },
})
</script>
