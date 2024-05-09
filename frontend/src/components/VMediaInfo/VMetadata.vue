<template>
  <dl v-if="isSm" class="metadata grid gap-8" :style="columnCount">
    <div v-for="datum in metadata" :key="datum.label">
      <VSourceProviderTooltip
        v-if="tooltipId(datum)"
        :described-by="tooltipId(datum)"
        class="label-regular -ms-1 mb-1 flex flex-row items-center ps-1"
        :datum="datum"
      />
      <dt v-else class="label-regular mb-1 flex flex-row ps-1">
        {{ $t(datum.label) }}
      </dt>
      <VMetadataValue
        :datum="datum"
        :class="{ '-ms-1': Boolean(tooltipId(datum)) }"
        @click="sendVisitSourceLinkEvent(datum.source)"
      />
    </div>
  </dl>
  <dl v-else class="grid grid-cols-[auto,1fr] gap-x-4 gap-y-2">
    <template v-for="datum in metadata">
      <VSourceProviderTooltip
        v-if="tooltipId(datum)"
        :key="datum.label"
        :described-by="tooltipId(datum)"
        class="label-regular -ms-1 flex flex-row items-center p-1 sm:ms-0 sm:py-0 sm:pe-0"
        :datum="datum"
      />
      <dt
        v-else
        :id="datum.label"
        :key="datum.label"
        class="label-regular flex flex-row pt-1"
      >
        {{ $t(datum.label) }}
      </dt>
      <VMetadataValue
        :key="`${datum.label}-value`"
        :datum="datum"
        @click="sendVisitSourceLinkEvent(datum.source)"
      />
    </template>
  </dl>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import type { Metadata } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"
import { useUiStore } from "~/stores/ui"

import VMetadataValue from "~/components/VMediaInfo/VMetadataValue.vue"
import VSourceProviderTooltip from "~/components/VMediaInfo/VSourceProviderTooltip.vue"

export default defineComponent({
  name: "VMetadata",
  components: { VSourceProviderTooltip, VMetadataValue },
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
    const tooltipId = (datum: Metadata): "source" | "provider" | "" => {
      if (
        datum.name &&
        (datum.name === "source" || datum.name === "provider")
      ) {
        return datum.name
      }
      return ""
    }

    const columnCount = computed(() => ({
      "--column-count": props.metadata.length,
    }))

    const { sendCustomEvent } = useAnalytics()
    const sendVisitSourceLinkEvent = (source?: string) => {
      if (!source) {
        return
      }
      sendCustomEvent("VISIT_SOURCE_LINK", {
        id: route.value.params.id,
        source,
      })
    }

    return {
      sendVisitSourceLinkEvent,
      tooltipId,
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
