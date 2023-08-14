<template>
  <dl>
    <div v-for="datum in metadata" :key="`${datum.label}`">
      <dt>{{ datum.label }}</dt>
      <dd>
        <VLink
          v-if="datum.url"
          :href="datum.url"
          class="text-pink"
          :show-external-icon="true"
          :external-link-inline="!isSm"
          @click="sendVisitSourceLinkEvent(datum.url, datum.isSource)"
          >{{ datum.value }}</VLink
        >
        <span v-else>{{ datum.value }}</span>
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

<style scoped>
dt,
dd {
  @apply text-sm md:text-base;
}

dd {
  @apply font-semibold;
}
dl {
  @apply flex flex-col gap-y-4;
}

dl div {
  @apply grid grid-cols-[30%,1fr] gap-x-4;
}
dl div dd {
  @apply max-w-full overflow-hidden;
}

@screen sm {
  dl {
    @apply flex-row flex-wrap gap-x-10 gap-y-5;
  }
  dl::after {
    content: "";
    flex: auto;
  }
  dl div {
    @apply flex flex-grow basis-0 flex-col gap-y-2;
  }
  dl div dt {
    @apply w-max;
  }
}
</style>
