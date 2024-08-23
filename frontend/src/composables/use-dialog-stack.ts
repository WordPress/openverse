import { computed, ref } from "vue"

const stack = ref<string[]>([])

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
