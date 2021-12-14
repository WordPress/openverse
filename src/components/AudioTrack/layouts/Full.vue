<template>
  <div class="full-track w-full">
    <slot name="controller" />

    <div
      class="flex flex-row flex-wrap items-top mx-6 sm:mx-16 my-4 sm:my-6 gap-6"
    >
      <slot name="play-pause" :size="isSmall ? 'small' : 'medium'" />

      <div class="audio-info order-2 sm:order-1 w-full sm:w-auto">
        <h1 class="text-base sm:text-3xl font-heading font-semibold">
          {{ audio.title }}
        </h1>
        <div
          class="subtitle mt-1 flex flex-col sm:flex-row sm:items-center gap-2"
        >
          <i18n
            as="span"
            path="audio-track.creator"
            class="font-semibold leading-snug"
          >
            <template #creator>
              <a
                class="text-pink hover:text-pink p-px rounded-sm focus:outline-none focus:ring focus:ring-pink"
                :href="audio.creator_url"
                >{{ audio.creator }}</a
              >
            </template>
          </i18n>

          <span v-if="!isSmall" class="text-dark-charcoal-70">{{
            $t('interpunct')
          }}</span>

          <div>{{ timeFmt(audio.duration) }}</div>
        </div>
      </div>

      <DownloadButton
        class="ms-auto order-1 sm:order-2"
        :formats="getFormats(audio)"
      />
    </div>
  </div>
</template>

<script>
import { computed } from '@nuxtjs/composition-api'

import DownloadButton from '~/components/DownloadButton.vue'

export default {
  name: 'Full',
  components: {
    DownloadButton,
  },
  props: ['audio', 'size'],
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
     * for DownloadButton
     * @param {AudioDetail} audio
     */
    const getFormats = (audio) => {
      let formats = [
        {
          extension_name: displayFormat(audio.provider, audio.filetype),
          download_url: audio.url,
        },
      ]
      if (audio.alt_files) {
        formats = formats.concat(
          audio.alt_files.map((altFile) => ({
            extension_name: displayFormat(audio.provider, altFile.filetype),
            download_url: altFile.url,
          }))
        )
      }
      return formats
    }

    const isSmall = computed(() => props.size === 's')

    return {
      timeFmt,
      getFormats,

      isSmall,
    }
  },
}
</script>

<style>
.full-track .waveform {
  @apply h-30 rounded-sm;
}

.full-track .play-pause {
  @apply rounded-sm;
}
</style>
