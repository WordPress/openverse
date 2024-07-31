<template>
  <div
    class="box-track group relative h-0 w-full rounded-sm bg-yellow-3-3 pt-full text-gray-12"
  >
    <div class="absolute inset-0 flex flex-col">
      <div class="info flex flex-grow flex-col justify-between px-4 pt-4">
        <h2
          class="label-bold line-clamp-3"
          :class="{ 'blur-text': shouldBlur }"
        >
          {{ shouldBlur ? $t("sensitiveContent.title.audio") : audio.title }}
        </h2>
        <div class="info">
          <VLicense
            class="hidden group-hover:block group-focus:block"
            hide-name
            :license="audio.license"
          />
          <div v-if="audio.category && !isSmall" class="label-regular mt-2">
            {{ categoryLabel }}
          </div>
        </div>
      </div>

      <div class="player flex h-12 flex-row items-end">
        <div class="flex-none p-2">
          <slot
            name="audio-control"
            size="small"
            layout="box"
            :is-tabbable="false"
          />
        </div>
        <p v-if="audio.category && isSmall" class="label-regular self-center">
          {{ categoryLabel }}
        </p>
        <slot
          v-if="!isSmall"
          name="controller"
          :features="[]"
          :is-tabbable="false"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { useI18n } from "#imports"

import { computed, defineComponent, type PropType } from "vue"

import type { AudioDetail } from "~/types/media"
import type { AudioSize } from "~/constants/audio"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"

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
      type: String as PropType<Extract<AudioSize, "s" | "l">>,
      required: true,
    },
  },
  setup(props) {
    const { t } = useI18n({ useScope: "global" })

    const isSmall = computed(() => props.size === "s")

    const categoryLabel = computed(() =>
      t(`filters.audioCategories.${props.audio.category}`)
    )

    const { isHidden: shouldBlur } = useSensitiveMedia(props.audio)
    return {
      isSmall,
      shouldBlur,

      categoryLabel,
    }
  },
})
</script>

<style scoped>
:deep(.waveform) {
  @apply h-10 flex-grow;
  --waveform-background-color: theme("colors.yellow-3-3");
}
</style>
