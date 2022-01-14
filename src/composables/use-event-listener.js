import {
  isRef,
  watch,
  onMounted,
  onBeforeUnmount,
  unref,
} from '@nuxtjs/composition-api'

/**
 * Use an event listener. Shamelessly stolen from https://logaretm.com/blog/my-favorite-5-vuejs-composables/#useeventlistener
 *
 * @param {import('@nuxtjs/composition-api').Ref<EventTarget | null> | EventTarget} target The target can be a reactive ref which adds flexibility
 * @param {string} event
 * @param {(e: Event) => void} handler
 * @param {any} options
 */
export function useEventListener(target, event, handler, options = {}) {
  // if it's a reactive ref, use a watcher
  if (isRef(target)) {
    watch(target, (value, oldValue) => {
      oldValue?.removeEventListener(event, handler)
      value?.addEventListener(event, handler, options)
    })
  } else {
    // otherwise, use the mounted hook
    onMounted(() => {
      target.addEventListener(event, handler, options)
    })
  }
  // clean it up
  onBeforeUnmount(() => {
    unref(target)?.removeEventListener(event, handler)
  })
}
