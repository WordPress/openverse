<template>
  <VIconButton
    v-bind="$attrs"
    :tabindex="layout === 'box' ? -1 : 0"
    class="play-pause flex-shrink-0 bg-dark-charcoal border-dark-charcoal text-white disabled:opacity-70 focus-visible:border-pink focus-visible:outline-none focus-visible:shadow-ring"
    :icon-props="{ iconPath: icon }"
    :aria-label="$t(label)"
    :button-props="buttonProps"
    @click.stop.prevent="handleClick"
  />
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { AudioLayout, AudioStatus } from '~/constants/audio'

import VIconButton from '~/components/VIconButton/VIconButton.vue'
import type { ButtonConnections, ButtonVariant } from '~/components/VButton.vue'

import playIcon from '~/assets/icons/play.svg'
import pauseIcon from '~/assets/icons/pause.svg'
import replayIcon from '~/assets/icons/replay.svg'

const statusVerbMap = {
  playing: 'pause',
  paused: 'play',
  played: 'replay',
} as const

const statusIconMap = {
  playing: pauseIcon,
  paused: playIcon,
  played: replayIcon,
} as const

const layoutConnectionsMap: Record<AudioLayout, ButtonConnections> = {
  row: 'end',
  global: 'all',
  box: 'none',
  full: 'none',
} as const

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

    /**
     * Sets the button variant to `plain-dangerous` to manually handle focus states.
     * Sets the connections (none-rounded corners) for the button based on the layout.
     */
    const buttonProps = computed(() => {
      const variant = 'plain-dangerous' as ButtonVariant

      return { variant, connections: layoutConnectionsMap[props.layout] }
    })

    const handleClick = () => {
      emit('toggle', isPlaying.value ? 'paused' : 'playing')
    }
    return {
      label,
      icon,
      buttonProps,

      handleClick,
    }
  },
})
</script>
