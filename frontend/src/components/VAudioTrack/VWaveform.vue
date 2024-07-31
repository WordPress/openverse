<template>
  <div
    v-bind="waveformAttributes"
    ref="el"
    class="waveform bg-background-var group/waveform text-gray-12 relative overflow-hidden focus-visible:outline-none"
    :style="heightProperties"
    :tabIndex="isTabbable && isInteractive ? 0 : -1"
    :aria-disabled="!isInteractive"
    :aria-label="$t('waveform.label')"
    v-on="eventHandlers"
  >
    <!-- Focus ring -->
    <svg
      v-if="isInteractive"
      class="shadow-ring-1 absolute inset-0 z-20 hidden h-full w-full group-focus/waveform:block"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="none"
    >
      <!-- Stroke is calculated from the centre of the path -->
      <rect
        v-if="waveformDimens.width && waveformDimens.height"
        class="stroke-pink-8"
        x="0.75"
        y="0.75"
        :width="waveformDimens.width - 1.5"
        :height="waveformDimens.height - 1.5"
        rx="2"
        fill="none"
        stroke-width="1.5"
      />
      <rect
        v-if="waveformDimens.width && waveformDimens.height"
        class="stroke-white"
        x="2"
        y="2"
        :width="waveformDimens.width - 4"
        :height="waveformDimens.height - 4"
        fill="none"
        stroke-width="1"
        rx="0.75"
      />
    </svg>

    <!-- Progress bar -->
    <svg
      class="absolute inset-0 h-full w-full"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="none"
    >
      <rect
        v-if="isReady"
        class="fill-yellow-3"
        x="0"
        y="0"
        :width="progressBarWidth"
        height="100%"
      />
    </svg>

    <!-- Bars -->
    <svg
      class="bars absolute bottom-0 w-full"
      :class="{ 'with-space': showDuration || showTimestamps }"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="none"
    >
      <rect
        v-for="(peak, index) in normalizedPeaks"
        :key="index"
        class="origin-bottom transform transition-transform duration-500"
        :class="[
          isReady ? 'scale-y-100' : 'scale-y-0',
          index <= seekIndex ? 'fill-black' : 'fill-gray-3-alpha',
        ]"
        :x="spaceBefore(index)"
        :y="spaceAbove(index)"
        :width="barWidth"
        :height="peak"
      />
    </svg>

    <!-- Focus bar -->
    <div
      v-if="isInteractive && isSeeking"
      class="absolute top-0 z-20 hidden h-full flex-col items-center justify-between bg-black group-focus/waveform:flex group-focus:flex"
      :style="{ width: `${barWidth}px`, left: `${progressBarWidth}px` }"
    >
      <div
        v-for="(classes, name) in {
          top: ['-translate-y-1/2'],
          bottom: ['translate-y-1/2'],
        }"
        :key="name"
        class="h-2 w-2 transform rounded-full bg-black"
        :class="classes"
      >
        &nbsp;
      </div>
    </div>

    <!-- Timestamps -->
    <template v-if="isReady">
      <template v-if="showTimestamps">
        <div
          ref="progressTimestampEl"
          class="progress timestamp z-10 transform"
          :class="[
            ...(isProgressTimestampCutoff
              ? ['bg-background-var']
              : ['bg-yellow-3', '-translate-x-full']),
          ]"
          :style="progressTimeLeft"
        >
          {{ timeFmt(progressTimestamp) }}
        </div>
        <div
          v-if="seekFrac"
          ref="seekTimestampEl"
          class="seek timestamp transform"
          :class="{ '-translate-x-full': !isSeekTimestampCutoff }"
          :style="seekTimeLeft"
        >
          {{ timeFmt(seekTimestamp) }}
        </div>
      </template>
      <div
        v-if="showDuration"
        class="duration timestamp bg-background-var right-0"
      >
        {{ timeFmt(duration) }}
      </div>
    </template>

    <!-- Message overlay -->
    <div
      v-else
      class="loading absolute inset-0 flex items-center justify-center text-xs font-bold"
    >
      {{ message }}
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref, toRef } from "vue"

import { downsampleArray, upsampleArray } from "~/utils/resampling"
import { timeFmt } from "~/utils/time-fmt"
import { useSeekable } from "~/composables/use-seekable"

import type { AudioFeature } from "~/constants/audio"

import useResizeObserver from "~/composables/use-resize-observer"

import { hash, rand as prng } from "~/utils/prng"

import { defineEvent } from "~/types/emits"

/**
 * If the duration is above this threshold, the progress timestamp will show ms.
 */
const MAX_SECONDS_FOR_MS = 1

/**
 * Renders an SVG representation of the waveform given a list of heights for the
 * bars.
 */
export default defineComponent({
  name: "VWaveform",
  props: {
    /**
     * an array of heights of the bars; The waveform will be generated with
     * bars of random length if the prop is not provided.
     */
    peaks: {
      type: Array as PropType<number[]>,
      required: false,
      validator: (val: unknown[]) =>
        val.every((item) => typeof item === "number"),
    },
    /**
     * the message to display instead of the waveform; This is useful when
     * displaying a loading or error state.
     */
    message: {
      type: String,
    },
    /**
     * the current play time of the audio track
     */
    currentTime: {
      type: Number,
      default: 0,
    },
    /**
     * the total play time of the audio track
     */
    duration: {
      type: Number as PropType<number>,
      default: 0,
    },
    /**
     * the fraction of the waveform height to use for the bars and timestamp;
     * The remaining space can be used to place other elements.
     */
    usableFrac: {
      type: Number,
      default: 1,
    },
    /**
     * selectively enable features in the waveform; Available features are
     * `'timestamps'`, `'duration'`, `'seek'`.
     */
    features: {
      type: Array as PropType<AudioFeature[]>,
      default: () => ["timestamps", "seek"],
    },
    /**
     * An object of notices to display when a feature is disabled.
     * `'timestamps'`, `'duration'`, `'seek'`.
     */
    featureNotices: {
      type: Object as PropType<Record<AudioFeature, boolean>>,
      default: () => ({}),
    },
    /**
     * Audio id to make the randomly-created peaks deterministic.
     */
    audioId: {
      type: String,
      required: true,
    },
    /**
     * whether the waveform can be focused by using the `Tab` key
     */
    isTabbable: {
      type: Boolean,
      default: true,
    },
    /**
     * whether the waveform should render as seeking when it is controlled by
     * the parent audio track
     */
    isParentSeeking: {
      type: Boolean,
      default: false,
    },
  },
  emits: {
    /**
     * Emitted when the waveform receives mouse events for seeking,
     * either single clicks on a specific part of the waveform,
     * or a click and drag.
     *
     * Also emitted when the waveform receives arrow key or home/end
     * keyboard events that also correspond to seeking.
     */
    seeked: defineEvent<[number]>(),
    "toggle-playback": defineEvent<[]>(),
    focus: defineEvent<[FocusEvent]>(),
    blur: defineEvent<[FocusEvent]>(),
  },
  setup(props, { emit }) {
    /* Utils */

    /**
     * Get the x-coordinate of the event with respect to the bounding box of the
     * waveform.
     * @param event - the event from which to get the position
     * @returns the x-position of the event inside the waveform
     */
    const getPosition = (event: MouseEvent): number => {
      return el.value
        ? event.clientX - el.value.getBoundingClientRect().x
        : event.clientX
    }
    /**
     * Get the x-position of the event with respect to the bounding box of the
     * waveform, as a fraction of the waveform width.
     * @param event - the event from which to get the position
     * @returns the x-position of the event as a fraction
     */
    const getPositionFrac = (event: MouseEvent): number => {
      const xPos = getPosition(event)
      return xPos / waveformDimens.value.width
    }
    /**
     * Get the number of peaks that will fit within the given width.
     * @param width - the number of pixels inside which to count peaks
     * @returns the number of peaks that can be accommodated
     */
    const getPeaksInWidth = (width: number): number => {
      return Math.floor((width - barGap) / (barWidth + barGap))
    }

    /* Element dimensions */

    const el = ref<HTMLElement | null>(null) // template ref
    const { dimens: waveformDimens } = useResizeObserver(el)

    /* Features */

    const showDuration = computed(() => props.features.includes("duration"))
    const showTimestamps = computed(() => props.features.includes("timestamps"))
    const isSeekable = computed(() => props.features.includes("seek"))

    /* State */

    const isReady = computed(() => !props.message)
    const isInteractive = computed(() => isSeekable.value && isReady.value)
    const isSeeking = computed(
      () => (!props.isTabbable && props.isParentSeeking) || isSelfSeeking.value
    )

    /* Resampling */

    const barWidth = 2
    const barGap = 2
    const peakCount = computed(() =>
      getPeaksInWidth(waveformDimens.value.width)
    )

    const createRandomPeaks = (audioId: string) => {
      const rand = prng(hash(audioId))
      return Array.from({ length: 100 }, () => rand())
    }
    const peaks = computed(() =>
      props.peaks?.length ? props.peaks : createRandomPeaks(props.audioId)
    )
    const normalizedPeaks = computed(() => {
      let samples = peaks.value

      const givenLength = samples.length
      const required = peakCount.value
      if (givenLength < required) {
        samples = upsampleArray(samples, required)
      } else if (givenLength > required) {
        samples = downsampleArray(samples, required)
      }

      return samples.map(
        (peak) => Math.max(peak, 0) * waveformDimens.value.height
      )
    })

    /* SVG drawing */

    const viewBox = computed(() =>
      [0, 0, waveformDimens.value.width, waveformDimens.value.height].join(" ")
    )
    const spaceBefore = (index: number) => index * barWidth + index * barGap
    const spaceAbove = (index: number) =>
      waveformDimens.value.height - normalizedPeaks.value[index]

    /* Progress bar */
    const progressBarWidth = computed(() => {
      const frac = isDragging.value ? seekFrac.value ?? 0 : currentFrac.value
      return waveformDimens.value.width * frac
    })

    /* Progress timestamp */

    const progressTimestampEl = ref<HTMLElement>()
    const progressTimestamp = computed(() =>
      isDragging.value ? seekTimestamp.value : props.currentTime
    )
    const isProgressTimestampCutoff = computed(() => {
      if (!progressTimestampEl.value) {
        return false
      }
      const barWidth = progressBarWidth.value
      const timestampWidth = progressTimestampEl.value.offsetWidth
      return barWidth < timestampWidth + 2
    })

    /**
     * Whether to show the ms part in the timestamps. True when the duration
     * is below MAX_SECONDS_FOR_MS seconds.
     */
    const showMsInTimestamp = computed(
      () =>
        Number.isFinite(props.duration) && props.duration < MAX_SECONDS_FOR_MS
    )

    /* Seek bar */

    const seekFrac = ref<number | null>(null)
    const seekBarWidth = computed(() => {
      const frac = seekFrac.value ?? currentFrac.value
      return waveformDimens.value.width * frac
    })
    const seekIndex = computed(() => getPeaksInWidth(seekBarWidth.value))

    /* Seek timestamp */

    const seekTimestampEl = ref<HTMLElement | null>(null)
    const seekTimestamp = computed(() =>
      seekFrac.value ? seekFrac.value * props.duration : props.duration
    )
    const isSeekTimestampCutoff = computed(() => {
      if (!seekTimestampEl.value) {
        return false
      }
      const barWidth = seekBarWidth.value
      const timestampWidth = seekTimestampEl.value.offsetWidth
      return barWidth < timestampWidth + 2
    })

    const { isSeeking: isSelfSeeking, ...seekable } = useSeekable({
      duration: toRef(props, "duration"),
      currentTime: toRef(props, "currentTime"),
      isSeekable,
      isReady,
      onSeek: (frac) => {
        clearSeekProgress()
        emit("seeked", frac)
      },
      onTogglePlayback: () => emit("toggle-playback"),
    })
    const waveformAttributes = computed(() => ({
      // ARIA slider attributes are only added when interactive
      ...(isInteractive.value ? seekable.attributes.value : {}),
    }))

    /* Seeking */

    /**
     * the seek jump length as a % of the track
     */
    const { currentFrac } = seekable.meta
    const setSeekProgress = (event: MouseEvent) => {
      seekFrac.value = getPositionFrac(event)
    }
    const clearSeekProgress = () => {
      seekFrac.value = null
    }
    const seek = (event: MouseEvent) => {
      emit("seeked", getPositionFrac(event))
    }

    /* Dragging */

    const dragThreshold = 2 // px
    let startPos: null | number = null
    const isDragging = ref(false)
    const handleMouseDown = (event: MouseEvent) => {
      if (!props.isTabbable) {
        // to prevent focus
        event.preventDefault()
      }
      isDragging.value = false
      startPos = getPosition(event)
      setSeekProgress(event)
    }
    const handleMouseMove = (event: MouseEvent) => {
      if (startPos) {
        const clickPos = getPosition(event)
        if (Math.abs(clickPos - startPos) > dragThreshold) {
          isDragging.value = true
        }
      }
      setSeekProgress(event)
    }
    const handleMouseUp = (event: MouseEvent) => {
      isDragging.value = false
      startPos = null
      seek(event)
    }
    const handleMouseLeave = () => {
      clearSeekProgress()
    }
    const handleClick = (event: MouseEvent) => {
      // Prevent event from bubbling to the parent anchor tag.
      event.stopPropagation()
      event.preventDefault()
    }
    const handleFocus = (event: FocusEvent) => {
      emit("focus", event)
    }
    const handleBlur = (event: FocusEvent) => {
      seekable.listeners.blur()
      emit("blur", event)
    }

    /* v-on */

    const eventHandlers = computed(() => {
      if (isInteractive.value) {
        return {
          mousedown: handleMouseDown,
          mousemove: handleMouseMove,
          mouseup: handleMouseUp,
          mouseleave: handleMouseLeave,
          click: handleClick,
          blur: handleBlur,
          focus: handleFocus,
          keydown: seekable.listeners.keydown,
        }
      } else {
        return {}
      }
    })

    const heightProperties = computed(() => ({
      "--usable-height": `${Math.floor(props.usableFrac * 100)}%`,
      "--unusable-height": `${Math.floor((1 - props.usableFrac) * 100)}%`,
    }))

    const progressTimeLeft = computed(() => ({
      "--progress-time-left": `${progressBarWidth.value}px`,
    }))

    const seekTimeLeft = computed(() => ({
      "--seek-time-left": `${seekBarWidth.value}px`,
    }))

    return {
      timeFmt,

      el, // template ref

      showDuration,
      showTimestamps,
      isSeekable,

      isReady,
      isInteractive,
      isSeeking,

      barWidth,
      normalizedPeaks,

      waveformDimens,
      viewBox,
      spaceBefore,
      spaceAbove,

      progressBarWidth,
      progressTimestamp,
      progressTimestampEl,
      isProgressTimestampCutoff,
      showMsInTimestamp,

      seekFrac,
      seekBarWidth,
      seekIndex,

      seekTimestamp,
      seekTimestampEl,
      isSeekTimestampCutoff,
      waveformAttributes,

      eventHandlers,

      heightProperties,
      progressTimeLeft,
      seekTimeLeft,
    }
  },
})
</script>

<style scoped>
.waveform {
  --v-background-color: var(
    --waveform-background-color,
    theme("colors.gray-1")
  );
}

.timestamp {
  @apply pointer-events-none absolute px-1 text-xs font-bold;
  top: calc(var(--unusable-height) + theme("spacing[0.5]"));
}

.bg-background-var {
  background-color: var(--v-background-color);
}

.bars {
  height: calc(var(--usable-height));
}

.bars.with-space {
  height: calc(var(--usable-height) - 1rem - 2 * theme("spacing[0.5]"));
}

.progress {
  left: var(--progress-time-left);
}

.seek {
  left: var(--seek-time-left);
}

.fill-gray-3-alpha {
  fill: rgba(48, 39, 46, 0.2);
}
</style>
