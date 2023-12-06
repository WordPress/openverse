import { computed, unref, Ref } from "vue"

import type { Media } from "~/types/media"

import { useUiStore } from "~/stores/ui"
import { useAnalytics } from "~/composables/use-analytics"

import type { SensitiveMediaVisibility } from "~/constants/content-safety"

type SensitiveFields = Pick<Media, "id" | "sensitivity" | "isSensitive">

/**
 * A helper composable for working with sensitive media.
 * Provides the current visibility of a sensitive media,
 * along with toggles for hiding/revealing the media.
 */
export function useSensitiveMedia(
  rawMedia: SensitiveFields | Ref<SensitiveFields> | null
) {
  const uiStore = useUiStore()
  const { sendCustomEvent } = useAnalytics()

  /**
   * The current state of a single sensitive media item.
   * Respects defaults from the site's filters and is
   * updated by user interactions.
   */
  const visibility = computed<SensitiveMediaVisibility>(() => {
    const media = unref(rawMedia)
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
    const media = unref(rawMedia)
    if (media && !uiStore.revealedSensitiveResults.includes(media.id)) {
      uiStore.revealedSensitiveResults.push(media.id)
      sendCustomEvent("UNBLUR_SENSITIVE_RESULT", {
        id: media.id,
        sensitivities: media.sensitivity.join(","),
      })
    }
  }

  function hide() {
    const media = unref(rawMedia)
    if (!media) {
      return
    }
    const index = uiStore.revealedSensitiveResults.indexOf(media.id)
    if (index > -1) {
      uiStore.revealedSensitiveResults.splice(index, 1)
    }
    sendCustomEvent("REBLUR_SENSITIVE_RESULT", {
      id: media.id,
      sensitivities: media.sensitivity.join(","),
    })
  }

  const isHidden = computed(() => {
    const media = unref(rawMedia)
    return (
      media &&
      uiStore.shouldBlurSensitive &&
      media.isSensitive &&
      visibility.value === "sensitive-hidden"
    )
  })

  const canBeHidden = computed(() => {
    const media = unref(rawMedia)
    return (
      media &&
      uiStore.shouldBlurSensitive &&
      media.isSensitive &&
      visibility.value === "sensitive-shown"
    )
  })

  return { visibility, reveal, hide, isHidden, canBeHidden }
}
