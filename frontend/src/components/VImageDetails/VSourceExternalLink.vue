<template>
  <VLink
    v-if="media.sourceName"
    :href="sourceUrl"
    class="text-pink"
    :send-external-link-click-event="false"
    @click="sendVisitSourceLinkEvent"
  >
    <span v-if="sourceNameParts.length > 1">{{ sourceNameParts[0] }}</span>

    <span class="whitespace-nowrap">
      {{ sourceNameParts[sourceNameParts.length - 1]
      }}<VIcon
        name="external-link"
        class="ms-1 inline-block"
        :size="4"
        rtl-flip
      />
    </span>
  </VLink>
</template>
<script lang="ts">
import { computed, defineComponent } from "vue"

import { useProviderStore } from "~/stores/provider"
import { useAnalytics } from "~/composables/use-analytics"
import type { SupportedMediaType } from "~/constants/media"

import VIcon from "~/components/VIcon/VIcon.vue"
import VLink from "~/components/VLink.vue"

import type { PropType } from "vue"

/**
 * This component is used to display the link to the media source landing page.
 * It tries to get the `sourceUrl` from the `providerStore` and if that fails,
 * it falls back to the `provider` link.
 *
 * The link has a special rendering to prevent the "external link" icon from
 * being orphaned on the last line of the link.
 */
export default defineComponent({
  name: "VSourceExternalLink",
  components: { VIcon, VLink },
  props: {
    media: {
      type: Object as PropType<{
        id: string
        sourceName?: string
        providerName?: string
        source?: string
        provider: string
        frontendMediaType: SupportedMediaType
      }>,
      required: true,
    },
  },
  setup(props) {
    const providerStore = useProviderStore()

    const sourceUrl = computed(() => {
      return providerStore.getSourceUrl(
        props.media.source ?? props.media.provider,
        props.media.frontendMediaType
      )
    })

    /**
     * To prevent the "external link" icon from being orphaned on a separate line,
     * combine the last word of the source name with the external link icon
     * in a span with whitespace set to nowrap.
     */
    const sourceNameParts = computed(() => {
      const name =
        props.media.sourceName ??
        props.media.providerName ??
        props.media.provider

      const lastSpaceIndex = name?.lastIndexOf(" ") ?? -1
      return lastSpaceIndex > -1
        ? [name.slice(0, lastSpaceIndex), name.slice(lastSpaceIndex + 1)]
        : [name]
    })

    const { sendCustomEvent } = useAnalytics()
    const sendVisitSourceLinkEvent = () => {
      if (!sourceUrl.value) return
      sendCustomEvent("VISIT_SOURCE_LINK", {
        id: props.media.id,
        url: sourceUrl.value,
      })
    }

    return { sourceNameParts, sourceUrl, sendVisitSourceLinkEvent }
  },
})
</script>
