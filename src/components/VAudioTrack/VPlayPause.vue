<template>
  <VIconButton
    v-bind="$attrs"
    :tabindex="layout === 'box' ? -1 : 0"
    class="play-pause flex-shrink-0 bg-dark-charcoal border-dark-charcoal text-white disabled:opacity-70 focus-visible:border-pink focus-visible:outline-none focus-visible:shadow-ring"
    :icon-props="icon === undefined ? undefined : { iconPath: icon }"
    :aria-label="$t(label)"
    :button-props="buttonProps"
    @click.stop.prevent="handleClick"
  >
    <template #default="{ iconSizeClasses }">
      <svg
        v-if="isLoading"
        class="loading p-2"
        :class="iconSizeClasses"
        xmlns="http://www.w3.org/2000/svg"
        overflow="visible"
        viewBox="0 0 12 12"
      >
        <circle cx="6" cy="6" r="6" vector-effect="non-scaling-stroke" />
        <path
          d="m 6 0 a 6 6 0 0 1 6 6"
          stroke="white"
          vector-effect="non-scaling-stroke"
        />
      </svg>
    </template>
  </VIconButton>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from '@nuxtjs/composition-api'

import type { AudioLayout, AudioStatus } from '~/constants/audio'
import { defineEvent } from '~/types/emits'

import VIconButton from '~/components/VIconButton/VIconButton.vue'
import type { ButtonConnections, ButtonVariant } from '~/components/VButton.vue'

import playIcon from '~/assets/icons/play.svg'
import pauseIcon from '~/assets/icons/pause.svg'
import replayIcon from '~/assets/icons/replay.svg'

const statusVerbMap = {
  playing: 'pause',
  paused: 'play',
  played: 'replay',
  loading: 'loading',
} as const

const statusIconMap = {
  playing: pauseIcon,
  paused: playIcon,
  played: replayIcon,
  loading: undefined,
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
  emits: {
    toggle: defineEvent<['paused' | 'playing']>(),
  },
  setup(props, { emit }) {
    const isPlaying = computed(() => props.status === 'playing')
    const isLoading = computed(() => props.status === 'loading')
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
      emit('toggle', isPlaying.value || isLoading.value ? 'paused' : 'playing')
    }
    return {
      label,
      icon,
      buttonProps,
      isLoading,

      handleClick,
    }
  },
})
</script>

<style scoped>
@keyframes spinAnimation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.loading circle,
.loading path {
  fill: transparent;
  stroke-width: 2px;
}

.loading circle {
  stroke: #595258;
}

.loading path {
  stroke-linecap: round;
  transform-origin: 50% 50%;
  animation: spinAnimation 1.4s linear infinite both;
}
</style>
