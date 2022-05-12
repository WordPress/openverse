<template>
  <article
    class="row-track flex flex-row"
    :class="[`size-${size}`, { 'items-start': isSmall }]"
  >
    <div
      class="relative flex-shrink-0 rounded-sm overflow-hidden"
      :class="isLarge ? 'w-30 me-6' : 'w-20 me-4'"
    >
      <VAudioThumbnail :audio="audio" />
      <div v-show="isSmall" class="absolute bottom-0 rtl:left-0 ltr:right-0">
        <slot name="play-pause" size="tiny" />
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
        <VLink
          :href="`/audio/${audio.id}`"
          class="block font-heading font-semibold line-clamp-2 md:line-clamp-1 text-dark-charcoal hover:text-dark-charcoal p-px rounded-sm focus:outline-none focus:ring focus:ring-pink"
          :class="{
            'text-2xl': isMedium || isLarge,
            'leading-snug': isSmall,
          }"
          >{{ audio.title }}</VLink
        >

        <div
          class="flex text-dark-charcoal-70 mt-2"
          :class="{
            'text-sr': isSmall,
            'leading-snug': isMedium || isLarge,
            'flex-col gap-2': isSmall || isMedium,
            'flex-row items-center': isLarge,
          }"
        >
          <div class="part-a">
            <i18n tag="span" path="audio-track.creator">
              <template #creator>{{ audio.creator }}</template> </i18n
            ><span v-show="isLarge" class="mx-2">{{ $t('interpunct') }}</span>
          </div>

          <div class="part-b inline-flex flex-row items-center">
            <span v-show="isSmall">
              <span
                class="inline-block text-dark-charcoal font-semibold bg-dark-charcoal-06 p-1 rounded-sm"
                >{{ timeFmt(audio.duration || 0) }}</span
              ><span class="mx-2">{{ $t('interpunct') }}</span>
            </span>

            <span v-if="audio.category">
              <span>{{ $t(`filters.audio-categories.${audio.category}`) }}</span
              ><span class="mx-2">{{ $t('interpunct') }}</span>
            </span>

            <VLicense :hide-name="isSmall" :license="audio.license" />
          </div>
        </div>
      </div>

      <div
        v-show="!isSmall"
        class="flex flex-row"
        :class="{
          'flex-grow': isMedium,
        }"
      >
        <slot name="play-pause" :size="isLarge ? 'medium' : 'large'" />
        <slot
          name="controller"
          :features="features"
          :feature-notices="featureNotices"
        />
      </div>
    </div>
  </article>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import { useBrowserIsBlink } from '~/composables/use-browser-detection'
import { useI18n } from '~/composables/use-i18n'
import type { AudioDetail } from '~/models/media'
import type { AudioSize } from '~/constants/audio'

import VAudioThumbnail from '~/components/VAudioThumbnail/VAudioThumbnail.vue'
import VLicense from '~/components/VLicense/VLicense.vue'
import VLink from '~/components/VLink.vue'

export default defineComponent({
  name: 'VRowLayout',
  components: {
    VAudioThumbnail,
    VLicense,
    VLink,
  },
  props: {
    audio: {
      type: Object as PropType<AudioDetail>,
      required: true,
    },
    size: {
      type: String as PropType<AudioSize>,
      required: false,
    },
  },
  setup(props) {
    /* Utils */
    const browserIsBlink = useBrowserIsBlink()
    const i18n = useI18n()

    const featureNotices: {
      timestamps?: string
      duration?: string
      seek?: string
    } = {}
    const features = ['timestamps', 'duration', 'seek']
    if (browserIsBlink && props.audio.source === 'jamendo') {
      features.pop()
      featureNotices.seek = i18n
        .t('audio-track.messages.blink_seek_disabled')
        .toString()
    }

    /**
     * Format the time as hh:mm:ss, dropping the hour part if it is zero.
     * @param ms - the number of milliseconds in the duration
     * @returns the duration in a human-friendly format
     */
    const timeFmt = (ms: number): string => {
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

      features,
      featureNotices,

      isSmall,
      isMedium,
      isLarge,
    }
  },
})
</script>

<style>
.row-track .play-pause {
  @apply rounded-ts-sm rounded-bs-sm flex-shrink-0;
}

.row-track .waveform {
  @apply flex-grow;
  --waveform-background-color: theme('colors.white');
}

.row-track .waveform {
  @apply rounded-te-sm rounded-be-sm;
}

.row-track.size-m .waveform {
  @apply h-20;
}

.row-track.size-l .waveform {
  @apply h-14;
}
</style>
