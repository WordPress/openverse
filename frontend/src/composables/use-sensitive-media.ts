import { computed } from "vue"

import type { Media } from "~/types/media"

import { useUiStore } from "~/stores/ui"

type SensitiveVisibilityState =
  | "non-sensitive"
  | "sensitive-shown"
  | "sensitive-hidden"

/**
 * A helper composable for working with sensitive media.
 * Provides the current visibility of a sensitive media,
 * along with toggles for hiding/revealing the media.
 */
export function useSensitiveMedia(
  media: Pick<Media, "id" | "isSensitive"> | null
) {
  const uiStore = useUiStore()

  /**
   * The current state of a single sensitive media item.
   * Respects defaults from the site's filters and is
   * updated by user interactions.
   */
  const visibility = computed<SensitiveVisibilityState>(() => {
    if (!media) {
      return "non-sensitive"
    } else if (media.isSensitive) {
      if (uiStore.revealedSensitiveResults.includes(media.id)) {
        return "sensitive-shown"
      } else {
        return uiStore.shouldBlurSensitive
          ? "sensitive-hidden"
          : "sensitive-shown"
      }
    } else {
      return "non-sensitive"
    }
  })

  function reveal() {
    if (media && !uiStore.revealedSensitiveResults.includes(media.id)) {
      uiStore.revealedSensitiveResults.push(media.id)
    }
  }

  function hide() {
    if (!media) return
    const index = uiStore.revealedSensitiveResults.indexOf(media.id)
    if (index > -1) {
      uiStore.revealedSensitiveResults.splice(index, 1)
    }
  }

  const isHidden = computed(
    () =>
      media &&
      uiStore.shouldBlurSensitive &&
      media.isSensitive &&
      visibility.value === "sensitive-hidden"
  )

  const canBeHidden = computed(
    () =>
      media &&
      uiStore.shouldBlurSensitive &&
      media.isSensitive &&
      visibility.value === "sensitive-shown"
  )

  return { visibility, reveal, hide, isHidden, canBeHidden }
}
