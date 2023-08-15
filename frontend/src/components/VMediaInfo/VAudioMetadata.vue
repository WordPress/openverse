<template>
  <dl>
    <div v-if="audio.audio_set">
      <dt>{{ $t("audioDetails.table.album") }}</dt>
      <dd>
        <VLink :href="audio.audio_set.foreign_landing_url">{{
          audio.audio_set.title
        }}</VLink>
      </dd>
    </div>
    <div v-if="audio.category">
      <dt>{{ $t("mediaDetails.information.category") }}</dt>
      <dd>
        {{ $t(`filters.audioCategories.${audio.category}`) }}
      </dd>
    </div>
    <div v-if="audio.sample_rate">
      <dt>
        {{ $t("audioDetails.table.sampleRate") }}
      </dt>
      <dd>
        {{ audio.sample_rate }}
      </dd>
    </div>
    <div v-if="audio.filetype">
      <dt>
        {{ $t("audioDetails.table.filetype") }}
      </dt>
      <dd>
        {{ audioFormats.toUpperCase() }}
      </dd>
    </div>
    <div>
      <dt>
        {{ $t("mediaDetails.providerLabel") }}
      </dt>
      <dd>
        <VLink :href="audio.foreign_landing_url">
          {{ audio.providerName }}
        </VLink>
      </dd>
    </div>
    <div v-if="audio.source && audio.sourceName !== audio.providerName">
      <dt>
        {{ $t("mediaDetails.sourceLabel") }}
      </dt>
      <dd>
        {{ audio.sourceName }}
      </dd>
    </div>
    <div v-if="audio.genres && audio.genres.length > 0">
      <dt>
        {{ $t("audioDetails.table.genre") }}
      </dt>
      <dd>
        {{ audio.genres.join(", ") }}
      </dd>
    </div>
  </dl>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AudioDetail } from "~/types/media"

import VLink from "~/components/VLink.vue"

export default defineComponent({
  name: "VAudioMetadata",
  components: { VLink },
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
  },
  setup(props) {
    const audioFormats = computed(() => {
      if (!props.audio.alt_files) return props.audio.filetype ?? ""
      const altFormats = props.audio.alt_files.map(
        (altFile) => altFile.filetype
      )
      if (props.audio.filetype) {
        altFormats.unshift(props.audio.filetype)
      }
      const uniqueFormats = new Set(altFormats)
      return [...uniqueFormats].join(", ")
    })

    return { audioFormats }
  },
})
</script>

<style scoped>
dl {
  @apply grid gap-4 lg:gap-5;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
}
dl div {
  display: flex;
  flex-direction: column;
}

dt {
  @apply text-base font-normal;
  display: inline-block;
}

dd {
  @apply pt-2 text-base font-semibold capitalize leading-snug;
}
</style>
