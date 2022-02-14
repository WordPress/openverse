<template>
  <div class="full-track w-full">
    <div class="bg-dark-charcoal-06 relative">
      <span
        v-if="currentTime > 0"
        class="pointer-events-none absolute h-full hidden md:block w-4 lg:w-10 left-0 bg-yellow"
        aria-hidden
      />
      <span
        v-if="status === 'played'"
        class="pointer-events-none absolute h-full hidden md:block w-4 lg:w-10 right-0 bg-yellow"
        aria-hidden
      />
      <div class="md:mx-4 lg:mx-10">
        <slot
          name="controller"
          :features="['timestamps', 'duration', 'seek']"
          :usable-frac="0.8"
        />
      </div>
    </div>
    <div
      class="flex flex-row flex-wrap lg:flex-nowrap items-top px-4 lg:px-0 lg:max-w-5xl mx-auto gap-6 mt-6"
    >
      <slot name="play-pause" :size="isSmall ? 'small' : 'medium'" />

      <div
        class="audio-info order-2 lg:order-1 w-full lg:w-auto flex flex-col justify-center"
      >
        <h1
          class="text-base lg:text-3xl font-heading font-semibold lg:line-clamp-2"
        >
          {{ audio.title }}
        </h1>
        <div
          class="subtitle mt-1 flex flex-col lg:flex-row lg:items-center gap-2"
        >
          <i18n
            as="span"
            path="audio-track.creator"
            class="font-semibold leading-snug"
          >
            <template #creator>
              <a
                class="p-px rounded-sm focus:outline-none focus:ring focus:ring-pink"
                :href="audio.creator_url"
              >
                {{ audio.creator }}
              </a>
            </template>
          </i18n>

          <span class="hidden lg:block text-dark-charcoal-70">{{
            $t('interpunct')
          }}</span>

          <div>{{ timeFmt(audio.duration) }}</div>
        </div>
      </div>

      <DownloadButton
        class="ms-auto order-1 lg:order-2"
        :formats="getFormats(audio)"
        :size="isSmall ? 'small' : 'medium'"
      />
    </div>
  </div>
</template>

<script>
import { computed, defineComponent } from '@nuxtjs/composition-api'

import DownloadButton from '~/components/DownloadButton.vue'

export default defineComponent({
  name: 'VFullLayout',
  components: {
    DownloadButton,
  },
  props: ['audio', 'size', 'status', 'currentTime'],
  setup(props) {
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

    /**
     * Returns specific display name for file format if there is a mapping for
     * provider's format display names (like Jamendo's `mp32` -> `MP3 V0`).
     * Otherwise, returns UpperCase format or ''
     * @param {string} provider
     * @param {string} [format]
     */
    const displayFormat = (provider, format) => {
      const filetypeMappings = {
        jamendo: { mp31: 'MP3 96kbs', mp32: 'MP3 V0' },
      }
      if (filetypeMappings[provider] && filetypeMappings[provider][format]) {
        return filetypeMappings[provider][format]
      }
      return format ? format.toUpperCase() : ''
    }

    /**
     * Creates a list of { extension_name, download_url } objects
     * for DownloadButton.
     *
     * If there are `alt_files` then just use that list. Otherwise,
     * create one using the preview URL.
     *
     * @param {AudioDetail} audio
     */
    const getFormats = (audio) => {
      if (audio.alt_files?.length) {
        return audio.alt_files.map((altFile) => ({
          extension_name: displayFormat(audio.provider, altFile.filetype),
          download_url: altFile.url,
        }))
      }

      return [
        {
          extension_name: displayFormat(audio.provider, audio.filetype),
          download_url: audio.url,
        },
      ]
    }

    const isSmall = computed(() => props.size === 's')

    return {
      timeFmt,
      getFormats,

      isSmall,
    }
  },
})
</script>

<style>
.full-track .waveform {
  @apply h-[185px] rounded-sm;
}

.full-track .play-pause {
  @apply rounded-sm;
}
</style>
