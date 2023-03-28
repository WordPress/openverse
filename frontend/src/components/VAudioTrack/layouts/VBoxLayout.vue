<template>
  <div :style="{ width }">
    <!-- The width is determined by the parent element if the 'size' property is not specified. -->
    <div
      class="box-track group relative h-0 w-full rounded-sm bg-yellow pt-full text-dark-charcoal"
    >
      <div class="absolute inset-0 flex flex-col">
        <div
          class="info flex flex-grow flex-col justify-between p-4"
          :class="{ 'pb-2': isDesktopWithSidebar }"
        >
          <h2
            class="description-bold leading-[1.3]"
            :class="isDesktopWithSidebar ? 'line-clamp-1' : 'line-clamp-3'"
          >
            {{ audio.title }}
          </h2>
          <div class="info">
            <VLicense
              class="hidden md:group-hover:block md:group-focus:block"
              :class="{ 'md:mb-2': !isDesktopWithSidebar }"
              hide-name
              :license="audio.license"
            />
            <div v-if="audio.category && !isDesktopWithSidebar">
              {{ categoryLabel }}
            </div>
          </div>
        </div>

        <div class="player hidden flex-row md:flex">
          <slot
            name="play-pause"
            size="small"
            layout="box"
            :is-tabbable="false"
          />
          <slot name="controller" :features="[]" :is-tabbable="false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useUiStore } from "~/stores/ui"

import type { AudioDetail } from "~/types/media"
import type { AudioSize } from "~/constants/audio"
import { useI18n } from "~/composables/use-i18n"

import VLicense from "~/components/VLicense/VLicense.vue"

export default defineComponent({
  name: "VBoxLayout",
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
    const uiStore = useUiStore()
    const i18n = useI18n()

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

    const isDesktopWithSidebar = computed(() => {
      return uiStore.isDesktopLayout && uiStore.isFilterVisible
    })

    return {
      width,
      categoryLabel,

      isDesktopWithSidebar,
    }
  },
})
</script>

<style>
.box-track .waveform {
  @apply flex-grow;
  --waveform-background-color: theme("colors.yellow");
}

.box-track .play-pause {
  @apply border-yellow bg-yellow text-dark-charcoal focus:border-pink;
}

.play-pause:hover {
  @apply border-dark-charcoal bg-dark-charcoal text-white;
}

.box-track .waveform {
  @apply h-10;
}
</style>
