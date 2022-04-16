<template>
  <section class="audio-info">
    <header class="flex flex-row justify-between items-center mb-6">
      <h4 class="text-base lg:text-3xl">
        {{ $t('audio-details.information') }}
      </h4>
      <VContentReportPopover :media="audio" />
    </header>

    <div class="flex flex-col md:flex-row items-start gap-6">
      <div class="w-[75px] h-[75px] lg:w-30 lg:h-30 rounded-sm overflow-hidden">
        <VAudioThumbnail :audio="audio" />
      </div>
      <div class="flex flex-col gap-4 lg:gap-6 flex-grow">
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
              <VLink :href="audio.audio_set.url">{{
                audio.audio_set.name
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
              {{ audio.filetype.toUpperCase() }}
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

<script>
import VLink from '~/components/VLink.vue'
import VAudioThumbnail from '~/components/VAudioThumbnail/VAudioThumbnail.vue'
import VMediaTag from '~/components/VMediaTag/VMediaTag.vue'

export default {
  name: 'VAudioDetails',
  components: { VAudioThumbnail, VLink, VMediaTag },
  props: ['audio'],
}
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
  font-weight: 400;
  display: inline-block;
}

dd {
  font-weight: bold;
}
</style>
