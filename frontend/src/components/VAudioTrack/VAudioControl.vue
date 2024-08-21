<script setup lang="ts">
/**
 * Displays the control for switching between the playing and paused states of
 * a media file.
 */
import { computed } from "vue"

import { AudioLayout, AudioStatus, statusVerbMap } from "~/constants/audio"
import type { ButtonConnections } from "~/types/button"

import { useHydrating } from "~/composables/use-hydrating"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

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
 * The mapping of audio control sizes to the VIconButton sizes
 * and the sizes of the contained icon.
 */
const sizes = {
  small: { button: "small", icon: 6 },
  medium: { button: "large", icon: 8 },
  large: { button: "larger", icon: 10 },
} as const

const props = withDefaults(
  defineProps<{
    /**
     * the current play status of the audio
     */
    status: AudioStatus
    /**
     * The size of the button. The size affects both the size of the button
     * itself and the icon inside it.
     */
    size: "small" | "medium" | "large"
    /**
     * The parent audio layout currently in use. The connections are determined
     * by the layout and the size of the button.
     */
    layout: AudioLayout
    /**
     * Whether the audio control button can be focused by using the `Tab` key
     */
    isTabbable?: boolean
  }>(),
  {
    layout: "full",
    isTabbable: true,
  }
)

const emit = defineEmits<{
  toggle: ["paused" | "playing"]
}>()

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
 * Set the connections (none-rounded corners) for the button based on the layout.
 */
const connections = computed(() => {
  return props.layout === "row" && props.size === "small"
    ? []
    : [...layoutConnectionsMap[props.layout]]
})

/** Convert the `audio-control` sizes to `VIconButton` sizes */
const buttonSize = computed(() => sizes[props.size].button)

const iSize = computed(() => sizes[props.size].icon)

const handleMouseDown = (event: MouseEvent) => {
  if (!props.isTabbable) {
    // to prevent focus
    event.preventDefault()
  }
}
const handleClick = () => {
  emit("toggle", isPlaying.value || isLoading.value ? "paused" : "playing")
}

const { doneHydrating } = useHydrating()
</script>

<template>
  <VIconButton
    :tabindex="isTabbable ? 0 : -1"
    class="audio-control"
    :size="buttonSize"
    :variant="layout === 'box' ? 'transparent-dark' : 'filled-dark'"
    :icon-props="icon === undefined ? undefined : { name: icon, size: iSize }"
    :label="$t(label)"
    :connections="connections"
    :disabled="!doneHydrating"
    @click.stop.prevent="handleClick"
    @mousedown="handleMouseDown"
  >
    <template #default>
      <svg
        v-if="isLoading"
        class="loading p-2"
        :class="`w-${iSize} h-${iSize}`"
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
