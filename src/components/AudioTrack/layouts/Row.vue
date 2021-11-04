<template>
  <article class="row-track flex flex-row" :class="`size-${size}`">
    <div class="flex-shrink-0" :class="isSmall ? 'w-20 me-4' : 'w-30 me-6'">
      <AudioThumbnail :audio="audio" />
    </div>
    <div
      class="flex"
      :class="isSmall ? 'flex-row gap-8' : 'flex-col justify-between'"
    >
      <div class="flex-shrink-0" :class="isSmall ? 'w-70' : ''">
        <NuxtLink
          :to="localePath(`/audio/${audio.id}`)"
          class="font-heading font-semibold text-2xl"
          >{{ audio.title }}</NuxtLink
        >

        <div
          class="flex leading-snug text-dark-charcoal-70 mt-2"
          :class="
            isSmall ? 'flex-col gap-2' : 'flex-row items-center justify-between'
          "
        >
          <div class="part-a">
            <i18n
              tag="span"
              class="font-semibold leading-snug"
              path="audio-track.creator"
            >
              <template #creator>{{ audio.creator }}</template>
            </i18n>
            <span v-if="!isSmall">
              {{ $t('interpunct') }} {{ timeFmt(audio.duration) }}
              <template v-if="audio.category">
                {{ $t('interpunct') }}
                {{ $t(`audio-categories.${audio.category}`) }}
              </template>
            </span>
          </div>

          <div class="part-b inline-flex space-x-1">
            <div v-if="isSmall">
              {{ timeFmt(audio.duration) }} {{ $t('interpunct') }}
              <template v-if="audio.category">
                {{ $t(`audio-categories.${audio.category}`) }}
                {{ $t('interpunct') }}
              </template>
            </div>
            <License class="inline" :license="audio.license" />
          </div>
        </div>
      </div>
      <div class="flex flex-row">
        <slot name="play-pause" />
        <slot name="controller" />
      </div>
    </div>
  </article>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'
import AudioThumbnail from '~/components/AudioThumbnail/AudioThumbnail.vue'
import License from '~/components/License/License.vue'

export default {
  name: 'Row',
  components: { AudioThumbnail, License },
  props: ['audio', 'size'],
  setup(props) {
    /* Utils */

    /**
     * Format the time as hh:mm:ss, dropping the hour part if it is zero.
     * @param {number} ms - the number of milliseconds in the duration
     * @returns {string} the duration in a human-friendly format
     */
    const timeFmt = (ms) => {
      if (ms) {
        const date = new Date(0)
        date.setSeconds(ms / 1e3)
        return date.toISOString().substr(11, 8).replace(/^00:/, '')
      }
      return '--:--'
    }

    const isSmall = computed(() => props.size === 's')

    return {
      timeFmt,
      isSmall,
    }
  },
}
</script>

<style>
.row-track .play-pause {
  @apply rounded-ts-sm rounded-bs-sm flex-shrink-0;
}

.row-track .waveform {
  @apply rounded-te-sm rounded-be-sm;
}

.row-track.size-s .play-pause {
  @apply h-20 w-20;
}

.row-track.size-s .waveform {
  @apply h-20;
}

.row-track.size-s .thumbnail {
  @apply rounded-ts-sm rounded-bs-sm overflow-hidden;
}

.row-track.size-m .play-pause {
  @apply h-14 w-14;
}

.row-track.size-m .waveform {
  @apply h-14;
}

.row-track.size-m .thumbnail {
  @apply rounded-sm overflow-hidden;
}
</style>
