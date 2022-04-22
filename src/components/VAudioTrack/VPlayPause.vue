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
import { defineComponent, PropType } from '@nuxtjs/composition-api'

import VIconButton from '~/components/VIconButton/VIconButton.vue'

import playIcon from '~/assets/icons/play.svg'
import pauseIcon from '~/assets/icons/pause.svg'
import replayIcon from '~/assets/icons/replay.svg'

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
      type: String as PropType<'playing' | 'paused' | 'played'>,
      required: true,
      validator: (val: unknown) =>
        ['playing', 'paused', 'played'].includes(val as string),
    },
    /**
     * The parent audio layout currently in use
     * @todo This type def should be extracted for reuse across components
     */
    layout: {
      type: String as PropType<'full' | 'box' | 'row' | 'global'>,
      default: 'full',
      validator: (val: unknown) =>
        ['full', 'box', 'row', 'global'].includes(val as string),
    },
  },
  data() {
    return {
      statusVerbMap: {
        playing: 'pause',
        paused: 'play',
        played: 'replay',
      },
      statusIconMap: {
        playing: pauseIcon,
        paused: playIcon,
        played: replayIcon,
      },
    }
  },
  computed: {
    isPlaying(): boolean {
      return this.status === 'playing'
    },
    /**
     * Get the button label based on the current status of the player.
     */
    label(): string {
      return `play-pause.${this.statusVerbMap[this.status]}`
    },
    /**
     * Get the button icon based on the current status of the player.
     */
    icon(): string {
      return this.statusIconMap[this.status]
    },
  },
  methods: {
    handleClick() {
      this.$emit('toggle', this.isPlaying ? 'paused' : 'playing')
    },
  },
})
</script>
