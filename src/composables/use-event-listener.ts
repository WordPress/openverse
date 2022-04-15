import {
  isRef,
  watch,
  onMounted,
  onBeforeUnmount,
  unref,
  Ref,
} from '@nuxtjs/composition-api'

const isComponentInstance = (o: unknown): o is { $el: unknown } =>
  !!o && typeof (o as { $el: unknown }).$el !== 'undefined'

export type MaybeRef<T> = Ref<T> | T

/**
 * Use an event listener.
 *
 * @see https://logaretm.com/blog/my-favorite-5-vuejs-composables/#useeventlistener
 */
export function useEventListener<T extends EventTarget>(
  target: MaybeRef<T | { $el: T }>,
  event: Parameters<T['addEventListener']>[0],
  handler: Parameters<T['addEventListener']>[1],
  options = {}
) {
  // if it's a reactive ref, use a watcher
  if (isRef(target)) {
    watch(target, (value, oldValue) => {
      const previous = isComponentInstance(oldValue) ? oldValue.$el : oldValue
      const current = isComponentInstance(value) ? value.$el : value
      previous?.removeEventListener(event, handler)
      current?.addEventListener(event, handler, options)
    })
  } else {
    // otherwise, use the mounted hook
    onMounted(() => {
      ;(isComponentInstance(target) ? target.$el : target).addEventListener(
        event,
        handler,
        options
      )
    })
  }
  // clean it up
  onBeforeUnmount(() => {
    const unreffed = unref(target)
    ;(isComponentInstance(unreffed)
      ? unreffed.$el
      : unreffed
    ).removeEventListener(event, handler)
  })
}
