<template>
  <section class="audio-info">
    <header class="mb-6 flex flex-row items-center justify-between">
      <h2 class="heading-6 md:heading-5">
        {{ $t('audio-details.information') }}
      </h2>
      <VContentReportPopover :media="audio" />
    </header>

    <div class="flex flex-col items-start gap-6 md:flex-row">
      <div class="h-[75px] w-[75px] overflow-hidden rounded-sm lg:h-30 lg:w-30">
        <VAudioThumbnail :audio="audio" />
      </div>
      <div class="flex flex-grow flex-col gap-4 lg:gap-6">
        <p v-if="audio.description" class="mb-6">{{ audio.description }}</p>
        <ul class="flex flex-wrap gap-2">
          <VMediaTag
            v-for="(tag, index) in audio.tags.filter((i) => !!i)"
            :key="index"
            tag="li"
          >
            {{ tag.name }}
          </VMediaTag>
        </ul>
        <dl v-if="audio">
          <div v-if="audio.audio_set">
            <dt>{{ $t('audio-details.table.album') }}</dt>
            <dd>
              <VLink :href="audio.audio_set.foreign_landing_url">{{
                audio.audio_set.title
              }}</VLink>
            </dd>
          </div>
          <div v-if="audio.category">
            <dt>{{ $t('audio-details.table.category') }}</dt>
            <dd>
              {{ $t(`filters.audio-categories.${audio.category}`) }}
            </dd>
          </div>
          <div v-if="audio.sample_rate">
            <dt>
              {{ $t('audio-details.table.sample-rate') }}
            </dt>
            <dd>
              {{ audio.sample_rate }}
            </dd>
          </div>
          <div v-if="audio.filetype">
            <dt>
              {{ $t('audio-details.table.filetype') }}
            </dt>
            <dd>
              {{ audioFormats.toUpperCase() }}
            </dd>
          </div>
          <div>
            <dt>
              {{ $t('audio-details.table.provider') }}
            </dt>
            <dd>
              <VLink :href="audio.foreign_landing_url">
                {{ audio.providerName }}
              </VLink>
            </dd>
          </div>
          <div v-if="audio.source && audio.sourceName !== audio.providerName">
            <dt>
              {{ $t('audio-details.table.source') }}
            </dt>
            <dd>
              {{ audio.sourceName }}
            </dd>
          </div>
          <div v-if="audio.genres && audio.genres.length > 0">
            <dt>
              {{ $t('audio-details.table.genre') }}
            </dt>
            <dd>
              {{ audio.genres.join(', ') }}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { AudioDetail } from '~/types/media'

import VAudioThumbnail from '~/components/VAudioThumbnail/VAudioThumbnail.vue'
import VContentReportPopover from '~/components/VContentReport/VContentReportPopover.vue'
import VLink from '~/components/VLink.vue'
import VMediaTag from '~/components/VMediaTag/VMediaTag.vue'

export default defineComponent({
  name: 'VAudioDetails',
  components: { VAudioThumbnail, VContentReportPopover, VLink, VMediaTag },
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
  },
  setup(props) {
    const audioFormats = computed(() => {
      if (!props.audio.alt_files) return props.audio.filetype
      const altFormats = props.audio.alt_files.map(
        (altFile) => altFile.filetype
      )
      altFormats.unshift(props.audio.filetype)
      const uniqueFormats = new Set(altFormats)
      return [...uniqueFormats].join(', ')
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
  @apply pt-2 text-sm text-base font-semibold capitalize leading-[130%];
}
</style>
