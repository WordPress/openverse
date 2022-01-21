<template>
  <div :style="{ width }">
    <!-- Should be wrapped by a fixed width parent -->
    <div
      class="box-track group relative bg-yellow h-0 w-full pt-full rounded-sm"
    >
      <div class="absolute inset-0 flex flex-col">
        <div class="info flex-grow flex flex-col justify-between p-4">
          <span class="font-heading font-semibold leading-snug line-clamp-3">{{
            audio.title
          }}</span>
          <div class="info">
            <VLicense
              class="mb-2 hidden md:group-hover:block md:group-focus:block"
              hide-name
              :license="audio.license"
            />
            <div>{{ $t(`audio-categories.${audio.category}`) }}</div>
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

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'

import VLicense from '~/components/License/VLicense.vue'

export default defineComponent({
  name: 'VBoxLayout',
  components: {
    VLicense,
  },
  props: ['audio', 'size'],
  setup(props) {
    const isSmall = computed(() => props.size === 's')

    const width = computed(() => {
      const magnitude = {
        l: 13.25,
        m: 12.25,
        s: 9.75,
      }[props.size ?? 'm']
      return `${magnitude}rem`
    })

    return {
      isSmall,

      width,
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
