<template>
  <dl v-if="isSm" class="metadata grid gap-8" :style="columnCount">
    <div v-for="datum in metadata" :key="`${datum.label}`">
      <dt class="label-regular mb-1 ps-1">{{ $t(datum.label) }}</dt>
      <VMetadataValue
        :datum="datum"
        @click="sendVisitSourceLinkEvent(datum.source)"
      />
    </div>
  </dl>
  <dl v-else class="grid grid-cols-[auto,1fr] gap-x-4 gap-y-2">
    <template v-for="datum in metadata" :key="datum.label">
      <dt class="label-regular pt-1">
        {{ $t(datum.label) }}
      </dt>
      <VMetadataValue
        :datum="datum"
        @click="sendVisitSourceLinkEvent(datum.source)"
      />
    </template>
  </dl>
</template>
<script lang="ts">
import { useRoute } from "#imports"

import { computed, defineComponent, PropType } from "vue"

import type { Metadata } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"
import { useUiStore } from "~/stores/ui"

import { firstParam } from "~/utils/query-utils"

import VMetadataValue from "~/components/VMediaInfo/VMetadataValue.vue"

export default defineComponent({
  name: "VMetadata",
  components: { VMetadataValue },
  props: {
    metadata: {
      type: Array as PropType<Metadata[]>,
      required: true,
    },
  },
  setup(props) {
    const route = useRoute()
    const uiStore = useUiStore()

    const isSm = computed(() => uiStore.isBreakpoint("sm"))

    const columnCount = computed(() => ({
      "--column-count": props.metadata.length,
    }))

    const { sendCustomEvent } = useAnalytics()
    const sendVisitSourceLinkEvent = (source?: string) => {
      if (!source) {
        return
      }
      const id = firstParam(route.params.id)
      sendCustomEvent("VISIT_SOURCE_LINK", {
        id,
        source,
      })
    }

    return {
      sendVisitSourceLinkEvent,
      isSm,
      columnCount,
    }
  },
})
</script>

<style scoped>
@screen sm {
  .metadata {
    grid-template-columns: repeat(var(--column-count, 4), fit-content(10rem));
  }
}
</style>
