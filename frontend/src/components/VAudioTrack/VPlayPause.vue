<template>
  <VOldIconButton
    v-bind="$attrs"
    :tabindex="isTabbable ? 0 : -1"
    class="play-pause flex-shrink-0 border-dark-charcoal bg-dark-charcoal text-white focus-visible:border-pink focus-visible:shadow-ring focus-visible:outline-none active:shadow-ring disabled:opacity-70"
    :icon-props="icon === undefined ? undefined : { name: icon }"
    :label="$t(label)"
    :button-props="buttonProps"
    @click.stop.prevent="handleClick"
    @mousedown="handleMouseDown"
  >
    <template #default="{ iconSize }">
      <svg
        v-if="isLoading"
        class="loading p-2"
        :class="`w-${iconSize} h-${iconSize}`"
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
  </VOldIconButton>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { AudioLayout, AudioStatus, statusVerbMap } from "~/constants/audio"
import { defineEvent } from "~/types/emits"
import type { ButtonConnections, ButtonVariant } from "~/types/button"

import VOldIconButton from "~/components/VIconButton/VOldIconButton.vue"

const statusIconMap = {
  playing: "pause",
  paused: "play",
  played: "replay",
  loading: undefined,
} as const

const layoutConnectionsMap: Record<AudioLayout, readonly ButtonConnections[]> =
  {
    row: ["end"],
    global: ["top", "end"],
    box: [],
    full: [],
  } as const

/**
 * Displays the control for switching between the playing and paused states of
 * a media file.
 */
export default defineComponent({
  name: "VPlayPause",
  components: { VOldIconButton },
  inheritAttrs: false,
  model: {
    prop: "status",
    event: "toggle",
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
      default: "full",
    },
    /**
     * whether the play-pause button can be focused by using the `Tab` key
     */
    isTabbable: {
      type: Boolean,
      default: true,
    },
  },
  emits: {
    toggle: defineEvent<["paused" | "playing"]>(),
  },
  setup(props, { emit }) {
    const isPlaying = computed(() => props.status === "playing")
    const isLoading = computed(() => props.status === "loading")
    /**
     * Get the button label based on the current status of the player.
     */
    const label = computed(() => `playPause.${statusVerbMap[props.status]}`)
    /**
     * Get the button icon based on the current status of the player.
     */
    const icon = computed(() => statusIconMap[props.status])

    /**
     * Sets the button variant to `plain--avoid` to manually handle focus states.
     * Sets the connections (none-rounded corners) for the button based on the layout.
     */
    const buttonProps = computed(() => {
      const variant = "plain--avoid" as ButtonVariant

      return { variant, connections: layoutConnectionsMap[props.layout] }
    })

    const handleMouseDown = (event: MouseEvent) => {
      if (!props.isTabbable) event.preventDefault() // to prevent focus
    }
    const handleClick = () => {
      emit("toggle", isPlaying.value || isLoading.value ? "paused" : "playing")
    }
    return {
      label,
      icon,
      buttonProps,
      isLoading,

      handleClick,
      handleMouseDown,
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
