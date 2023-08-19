<template>
  <dl :class="media.frontendMediaType">
    <div v-for="datum in metadata" :key="`${datum.label}`">
      <dt>{{ datum.label }}</dt>
      <dd>
        <VLink v-if="datum.url" :href="datum.url" class="text-pink">{{
          datum.value
        }}</VLink>
        <span v-else>{{ datum.value }}</span>
      </dd>
    </div>
  </dl>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"
import { useUiStore } from "~/stores/ui"

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

    return {
      isSm,
    }
  },
})
</script>

<style scoped>
dl.image {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  grid-gap: 1rem;
}

.image dt,
.image dd {
  @apply text-sm md:text-base;
}

.image dd {
  @apply mt-2 font-semibold;
}

dl.audio {
  @apply grid gap-4 lg:gap-5;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
}
dl.audio div {
  display: flex;
  flex-direction: column;
}

.audio dt {
  @apply text-base font-normal;
  display: inline-block;
}

.audio dd {
  @apply pt-2 text-base font-semibold capitalize leading-snug;
}
</style>
