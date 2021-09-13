<template>
  <div class="row-track flex flex-row" :class="`size-${size}`">
    <AudioThumb
      class="flex-shrink-0"
      :class="isSmall ? 'w-20 mr-4' : 'w-30 mr-6'"
      :audio="audio"
    />
    <div class="flex" :class="isSmall ? 'flex-row gap-8' : 'flex-col gap-4'">
      <div class="flex-shrink-0">
        <p class="font-heading font-semibold text-2xl">{{ audio.title }}</p>

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
              • {{ audio.duration }} • {{ audio.category }}
            </span>
          </div>

          <div class="part-b">
            <template v-if="isSmall">
              {{ audio.duration }} • {{ audio.category }} •
            </template>
            {{ audio.license }}
          </div>
        </div>
      </div>
      <div class="flex flex-row">
        <slot name="play-pause" />
        <slot name="controller" />
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'
import AudioThumb from '~/components/AudioTrack/AudioThumb.vue'

export default {
  name: 'Row',
  components: { AudioThumb },
  props: ['audio', 'size'],
  setup(props) {
    const isSmall = computed(() => props.size === 's')

    return {
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
