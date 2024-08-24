import { computed, ref } from "vue"

const stack = ref<string[]>([])

/**
 * This composable allows displaying multiple dialogs on top of each other,
 * and routing the events to the active, top-most dialog.
 */
export const useDialogStack = () => {
  const push = (id: string) => {
    stack.value.push(id)
  }
  const pop = () => {
    stack.value.pop()
  }
  const clear = () => {
    stack.value = []
  }
  const indexOf = (id: string) => {
    return stack.value.indexOf(id)
  }

  /**
   * The top-level dialog in the UI that intercepts 'outside' events.
   */
  const activeDialog = computed(() => stack.value[stack.value.length - 1])

  return {
    stack,
    push,
    pop,
    clear,
    indexOf,
    activeDialog,
  }
}
