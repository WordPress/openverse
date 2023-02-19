import {
  getCurrentInstance,
  nextTick,
  onMounted,
} from "@nuxtjs/composition-api"

export function tryOnMounted(fn: () => void, sync = true) {
  if (getCurrentInstance()) {
    onMounted(fn)
  } else if (sync) {
    fn()
  } else {
    nextTick(fn)
  }
}
