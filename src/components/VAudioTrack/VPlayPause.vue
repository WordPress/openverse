<template>
  <VIconButton
    v-bind="$attrs"
    :tabindex="layout === 'box' ? -1 : 0"
    class="play-pause flex-shrink-0 bg-dark-charcoal border-dark-charcoal text-white disabled:opacity-70 focus-visible:border-pink focus-visible:outline-none focus-visible:shadow-ring"
    :icon-props="{ iconPath: icon }"
    :aria-label="$t(label)"
    :button-props="{ variant: 'plain-dangerous' }"
    @click.stop.prevent="handleClick"
  />
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { AudioLayout, AudioStatus } from '~/constants/audio'

import VIconButton from '~/components/VIconButton/VIconButton.vue'

import playIcon from '~/assets/icons/play.svg'
import pauseIcon from '~/assets/icons/pause.svg'
import replayIcon from '~/assets/icons/replay.svg'

const statusVerbMap = {
  playing: 'pause',
  paused: 'play',
  played: 'replay',
}
const statusIconMap = {
  playing: pauseIcon,
  paused: playIcon,
  played: replayIcon,
}
/**
 * Displays the control for switching between the playing and paused states of
 * a media file.
 */
export default defineComponent({
  name: 'VPlayPause',
  components: { VIconButton },
  inheritAttrs: false,
  model: {
    prop: 'status',
    event: 'toggle',
  },
  props: {
    /**
     * the current play status of the audio
     */
    status: {
      type: String as PropType<AudioStatus>,
      required: true,
    },
    /**
     * The parent audio layout currently in use
     */
    layout: {
      type: String as PropType<AudioLayout>,
      default: 'full',
    },
  },
  setup(props, { emit }) {
    const isPlaying = computed(() => props.status === 'playing')
    /**
     * Get the button label based on the current status of the player.
     */
    const label = computed(() => `play-pause.${statusVerbMap[props.status]}`)
    /**
     * Get the button icon based on the current status of the player.
     */
    const icon = computed(() => statusIconMap[props.status])
    const handleClick = () => {
      emit('toggle', isPlaying.value ? 'paused' : 'playing')
    }
    return {
      label,
      icon,

      handleClick,
    }
  },
})
</script>
