<template>
  <article class="row-track flex flex-row" :class="`size-${size}`">
    <div
      class="relative flex-shrink-0 rounded-sm overflow-hidden"
      :class="isLarge ? 'w-30 me-6' : 'w-20 me-4'"
    >
      <AudioThumbnail :audio="audio" />
      <div v-if="isSmall" class="absolute bottom-0 end-0">
        <slot name="play-pause" />
      </div>
    </div>

    <div
      class="flex-grow"
      :class="{
        'flex flex-row gap-8': isMedium,
        'flex flex-col justify-between': isLarge,
      }"
    >
      <div class="flex-shrink-0" :class="{ 'w-70': isMedium }">
        <NuxtLink
          :to="localePath(`/audio/${audio.id}`)"
          class="font-heading font-semibold text-dark-charcoal hover:text-dark-charcoal"
          :class="{
            'text-2xl': isMedium || isLarge,
            'leading-snug': isSmall,
          }"
          >{{ audio.title }}</NuxtLink
        >

        <div
          class="flex text-dark-charcoal-70 mt-2"
          :class="{
            'text-sr': isSmall,
            'leading-snug': isMedium || isLarge,
            'flex-col gap-2': isSmall || isMedium,
            'flex-row items-center justify-between': isLarge,
          }"
        >
          <div class="part-a">
            <i18n tag="span" class="font-semibold" path="audio-track.creator">
              <template #creator>{{ audio.creator }}</template>
            </i18n>
            <span v-if="isSmall || isLarge">
              {{ $t('interpunct') }} {{ timeFmt(audio.duration) }}
              <template v-if="audio.category">
                {{ $t('interpunct') }}
                {{ $t(`audio-categories.${audio.category}`) }}
              </template>
            </span>
          </div>

          <div class="part-b inline-flex space-x-1">
            <div v-if="isMedium">
              {{ timeFmt(audio.duration) }} {{ $t('interpunct') }}
              <template v-if="audio.category">
                {{ $t(`audio-categories.${audio.category}`) }}
                {{ $t('interpunct') }}
              </template>
            </div>
            <VLicense :license="audio.license" />
          </div>
        </div>
      </div>

      <div
        class="flex flex-row"
        :class="{
          hidden: isSmall,
          'flex-grow': isMedium,
        }"
      >
        <slot name="play-pause" />
        <slot name="controller" />
      </div>
    </div>
  </article>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'
import AudioThumbnail from '~/components/AudioThumbnail/AudioThumbnail.vue'
import VLicense from '~/components/License/VLicense.vue'

export default {
  name: 'Row',
  components: { AudioThumbnail, VLicense },
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
    const isMedium = computed(() => props.size === 'm')
    const isLarge = computed(() => props.size === 'l')

    return {
      timeFmt,

      isSmall,
      isMedium,
      isLarge,
    }
  },
}
</script>

<style>
.row-track .play-pause {
  @apply rounded-ts-sm rounded-bs-sm flex-shrink-0;
}

.row-track .audio-controller {
  @apply flex-grow;
}

.row-track .waveform {
  @apply rounded-te-sm rounded-be-sm;
}

.row-track.size-m .play-pause {
  @apply h-20 w-20;
}

.row-track.size-m .waveform {
  @apply h-20;
}

.row-track.size-l .play-pause {
  @apply h-14 w-14;
}

.row-track.size-l .waveform {
  @apply h-14;
}
</style>
