import { computed, ref } from "vue"

import { useUiStore } from "~/stores/ui"

/**
 * Composable that handles showing and hiding of the snackbar
 * with instructions for audio interactions.
 *
 * Shows the snackbar when the user focuses the first audio track.
 * Hides the snackbar when the user interacts with it (seeks or clicks on play button).
 */
export const useAudioSnackbar = () => {
  const isMouseDown = ref(false)
  const handleMouseDown = () => {
    isMouseDown.value = true
  }

  const show = () => {
    if (isMouseDown.value) {
      // The audio player was clicked to open the single result view, not
      // focused via keyboard.
      isMouseDown.value = false
    } else {
      useUiStore().showInstructionsSnackbar()
    }
  }
  const hide = () => {
    useUiStore().hideInstructionsSnackbar()
  }
  const dismiss = () => {
    useUiStore().dismissInstructionsSnackbar()
  }

  const isVisible = computed(() => useUiStore().areInstructionsVisible)

  return {
    isVisible,
    show,
    hide,
    dismiss,
    handleMouseDown,
    isMouseDown,
  }
}
