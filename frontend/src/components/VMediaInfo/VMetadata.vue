<template>
  <dl class="flex flex-col gap-y-6">
    <div v-for="datum in metadata" :key="datum.label.toString()">
      <dt>{{ datum.label }}</dt>
      <dd>
        <VSourceExternalLink
          v-if="datum.component === 'VSourceExternalLink'"
          :media="media"
        />
        <VLink v-else-if="datum.url" :href="datum.url">{{ datum.value }}</VLink>
        <span v-else>{{ datum.value }}</span>
      </dd>
    </div>
  </dl>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioDetail, ImageDetail, Metadata } from "~/types/media"

import VSourceExternalLink from "~/components/VImageDetails/VSourceExternalLink.vue"
import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VMetadata",
  components: { VLink, VSourceExternalLink },
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

dl div {
  @apply flex flex-row;
}

dl div > dt {
  @apply basis-1/3;
}

@screen sm {
  dl {
    @apply grid gap-4;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
  dl div {
    @apply flex flex-col gap-y-2;
  }
}
</style>
