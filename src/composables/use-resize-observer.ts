import { ref, onMounted, onBeforeUnmount } from '@nuxtjs/composition-api'

import type { Ref } from '@nuxtjs/composition-api'

/**
 * Configure a `ResizeObserver` to observe the given `HTMLElement` and update
 * the dimensions whenever it is resized.
 *
 * @param elem - the ref pointing to the `HTMLElement` to observe
 */
export default function useResizeObserver(elem: Ref<HTMLElement | null>) {
  const dimens = ref({ width: 0, height: 0 })
  const updateDimens = () => {
    dimens.value = {
      width: elem.value?.clientWidth || 0,
      height: elem.value?.clientHeight || 0,
    }
  }

  let observer: ResizeObserver | undefined
  onMounted(() => {
    if (window.ResizeObserver && elem.value) {
      observer = new ResizeObserver(updateDimens)
      observer.observe(elem.value)
    }
    updateDimens()
  })
  onBeforeUnmount(() => {
    if (observer) {
      observer.disconnect()
    }
  })

  return { dimens }
}
