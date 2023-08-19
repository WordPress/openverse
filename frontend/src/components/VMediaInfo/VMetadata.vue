<template>
  <dl
    class="flex flex-col gap-y-4 sm:flex-row sm:flex-wrap sm:gap-x-10 sm:gap-y-5 sm:after:flex-auto sm:after:content-['']"
  >
    <div
      v-for="datum in metadata"
      :key="`${datum.label}`"
      class="grid grid-cols-[30%,1fr] gap-x-4 text-sm sm:flex sm:basis-0 sm:flex-col sm:gap-y-2 md:text-base"
    >
      <dt class="sm:w-max">{{ $t(datum.label) }}</dt>
      <dd class="max-w-full overflow-hidden font-semibold">
        <VLink
          v-if="datum.url"
          :href="datum.url"
          class="text-pink"
          show-external-icon
          @click="sendVisitSourceLinkEvent(datum.source)"
          >{{ datum.value }}</VLink
        >
        <span v-else class="w-auto sm:flex sm:w-max">{{ datum.value }}</span>
      </dd>
    </div>
  </dl>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"

import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VMetadata",
  components: { VLink },
  props: {
    media: {
      type: Object as PropType<AudioDetail | ImageDetail>,
      required: true,
    },
    metadata: {
      type: Array as PropType<Metadata[]>,
      required: true,
    },
  },
  setup() {
    const route = useRoute()

    const { sendCustomEvent } = useAnalytics()
    const sendVisitSourceLinkEvent = (source?: string) => {
      if (!source) return
      sendCustomEvent("VISIT_SOURCE_LINK", {
        id: route.value.params.id,
        source,
      })
    }

    return {
      sendVisitSourceLinkEvent,
    }
  },
})
</script>
