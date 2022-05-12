<template>
  <div :style="{ width }">
    <!-- The width is determined by the parent element if the 'size' property is not specified. -->
    <div
      class="box-track group relative bg-yellow h-0 w-full pt-full rounded-sm text-dark-blue"
    >
      <div class="absolute inset-0 flex flex-col">
        <div class="info flex-grow flex flex-col justify-between p-4">
          <h2
            class="font-heading font-semibold leading-snug line-clamp-3 text-base"
          >
            {{ audio.title }}
          </h2>
          <div class="info">
            <VLicense
              class="mb-2 hidden md:group-hover:block md:group-focus:block"
              hide-name
              :license="audio.license"
            />
            <div v-if="audio.category">
              {{ categoryLabel }}
            </div>
          </div>
        </div>

        <div class="hidden player md:flex flex-row">
          <slot name="play-pause" size="small" layout="box" />
          <slot name="controller" :features="[]" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { AudioDetail } from '~/models/media'
import type { AudioSize } from '~/constants/audio'
import { useI18n } from '~/composables/use-i18n'

import VLicense from '~/components/VLicense/VLicense.vue'

export default defineComponent({
  name: 'VBoxLayout',
  components: {
    VLicense,
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
    const i18n = useI18n()
    const isSmall = computed(() => props.size === 's')

    const width = computed(() => {
      const magnitudes = {
        l: 13.25,
        m: 12.25,
        s: 9.75,
      }

      return props.size ? `${magnitudes[props.size]}rem` : undefined
    })
    const categoryLabel = computed(() =>
      i18n.t(`filters.audio-categories.${props.audio.category}`).toString()
    )

    return {
      isSmall,

      width,
      categoryLabel,
    }
  },
})
</script>

<style>
.box-track .waveform {
  @apply flex-grow;
  --waveform-background-color: theme('colors.yellow');
}

.box-track .play-pause {
  @apply text-dark-charcoal bg-yellow border-yellow focus:border-pink;
}

.box-track .waveform {
  @apply h-10;
}
</style>
