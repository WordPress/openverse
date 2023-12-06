import { computed, ToRefs, ref } from "vue"

import { useI18n } from "~/composables/use-i18n"
import { keycodes } from "~/constants/key-codes"

export interface UseSeekableOptions
  extends ToRefs<{
    duration: number
    currentTime: number
    isSeekable: boolean
    isReady: boolean
  }> {
  onSeek: (frac: number) => void
  onTogglePlayback: () => void
}

export const useSeekable = ({
  duration,
  currentTime,
  isSeekable,
  isReady,
  onSeek,
  onTogglePlayback,
}: UseSeekableOptions) => {
  const i18n = useI18n()

  const attributes = computed(() => ({
    "aria-role": "slider",
    "aria-valuemax": duration.value,
    "aria-valuenow": currentTime.value,
    "aria-valuetext": i18n
      .tc("waveform.currentTime", currentTime.value, {
        time: currentTime.value,
      })
      .toString(),
    "aria-orientation": "horizontal" as const,
    "aria-valuemin": "0",
  }))

  const seekDelta = 1 // seconds
  const modSeekDelta = 15 // seconds
  const modSeekDeltaFrac = computed(() =>
    isReady.value ? modSeekDelta / duration.value : 0
  )
  const seekDeltaFrac = computed(() =>
    isReady.value ? seekDelta / duration.value : 0
  )
  const currentFrac = computed(() =>
    isReady.value ? currentTime.value / duration.value : 0
  )
  const isSeeking = ref(false)

  const handleArrowKeys = (event: KeyboardEvent) => {
    const { key, shiftKey, metaKey } = event
    if (metaKey) {
      // Always false on Windows
      onSeek(key.includes("Left") ? 0 : 1)
    } else {
      const direction = key.includes("Left") ? -1 : 1
      const magnitude = shiftKey ? modSeekDeltaFrac.value : seekDeltaFrac.value
      const delta = magnitude * direction
      onSeek(currentFrac.value + delta)
    }
  }

  const arrowKeys = [keycodes.ArrowLeft, keycodes.ArrowRight]
  const seekingKeys = [...arrowKeys, keycodes.Home, keycodes.End]
  const handledKeys = [...seekingKeys, keycodes.Spacebar]

  /**
   * This composable handles space bar for toggling playback.
   * If `isSeekable` is true, it also handles `seekingKeys`.
   */
  const willBeHandled = (event: KeyboardEvent) => {
    return isSeekable.value
      ? (handledKeys as string[]).includes(event.key)
      : event.key === keycodes.Spacebar
  }

  const handleKeys = (event: KeyboardEvent) => {
    if (!willBeHandled(event)) {
      return
    }

    event.preventDefault()

    isSeeking.value = (seekingKeys as string[]).includes(event.key)

    if ((arrowKeys as string[]).includes(event.key)) {
      return handleArrowKeys(event)
    }
    if (event.key === keycodes.Home) {
      return onSeek(0)
    }
    if (event.key === keycodes.End) {
      return onSeek(1)
    }
    if (event.key === keycodes.Spacebar) {
      return onTogglePlayback()
    }
  }
  const handleBlur = () => {
    isSeeking.value = false
  }

  const listeners = {
    keydown: handleKeys,
    blur: handleBlur,
  }

  const meta = {
    modSeekDeltaFrac,
    seekDeltaFrac,
    currentFrac,
  }

  return { attributes, listeners, meta, willBeHandled, isSeeking }
}
