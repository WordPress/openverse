<template>
  <dl
    class="flex flex-col gap-y-4 sm:flex-row sm:flex-wrap sm:gap-x-10 sm:gap-y-5 sm:after:flex-auto sm:after:content-['']"
  >
    <div
      v-for="datum in metadata"
      :key="`${datum.label}`"
      class="grid grid-cols-[30%,1fr] gap-x-4 text-sm sm:flex sm:basis-0 sm:flex-col sm:gap-y-2 md:text-base"
    >
      <dt class="sm:w-max">{{ datum.label }}</dt>
      <dd class="max-w-full overflow-hidden font-semibold">
        <VLink
          v-if="datum.url"
          :href="datum.url"
          class="text-pink"
          show-external-icon
          :external-link-inline="!isSm"
          @click="sendVisitSourceLinkEvent(datum.url, datum.isSource)"
          >{{ datum.value }}</VLink
        >
        <span v-else class="w-auto sm:flex sm:w-max">{{ datum.value }}</span>
      </dd>
    </div>
  </dl>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"
import { useUiStore } from "~/stores/ui"
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
    const uiStore = useUiStore()
    const isSm = computed(() => uiStore.isBreakpoint("sm"))

    const route = useRoute()

    const { sendCustomEvent } = useAnalytics()
    const sendVisitSourceLinkEvent = (url?: string, isSource?: boolean) => {
      if (!url || !isSource) return
      sendCustomEvent("VISIT_SOURCE_LINK", {
        id: route.value.params.id,
        url,
      })
    }

    return {
      sendVisitSourceLinkEvent,
      isSm,
    }
  },
})
</script>
