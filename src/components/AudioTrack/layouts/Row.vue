<template>
  <article class="row-track flex flex-row" :class="`size-${size}`">
    <AudioThumb
      class="flex-shrink-0"
      :class="isSmall ? 'w-20 mr-4' : 'w-30 mr-6'"
      :audio="audio"
    />
    <div
      class="flex"
      :class="isSmall ? 'flex-row gap-8' : 'flex-col justify-between'"
    >
      <div class="flex-shrink-0">
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
              • {{ timeFmt(audio.duration) }} •
              {{ $t(`audio-categories.${audio.category}`) }}
            </span>
          </div>

          <div class="part-b">
            <template v-if="isSmall">
              {{ timeFmt(audio.duration) }} •
              {{ $t(`audio-categories.${audio.category}`) }} •
            </template>
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
import AudioThumb from '~/components/AudioTrack/AudioThumb.vue'
import License from '~/components/License/License.vue'

export default {
  name: 'Row',
  components: { AudioThumb, License },
  props: ['audio', 'size'],
  setup(props) {
    /* Utils */

    /**
     * Format the time as hh:mm:ss, dropping the hour part if it is zero.
     * @param {number} ms - the number of milliseconds in the duration
     * @returns {string} the duration in a human-friendly format
     */
    const timeFmt = (ms) => {
      const date = new Date(0)
      date.setSeconds(ms / 1e3)
      return date.toISOString().substr(11, 8).replace(/^00:/, '')
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
.play-pause {
  @apply rounded-tl-sm rounded-bl-sm flex-shrink-0;
}

.waveform {
  @apply rounded-tr-sm rounded-br-sm;
}

.size-s .play-pause {
  @apply h-20 w-20;
}

.size-s .waveform {
  @apply h-20;
}

.size-m .play-pause {
  @apply h-14 w-14;
}

.size-m .waveform {
  @apply h-14;
}
</style>
