import { ref, onMounted, onBeforeUnmount } from "@nuxtjs/composition-api"

import type { Ref } from "@nuxtjs/composition-api"

interface Options {
  initialWidth?: number
  initialHeight?: number
}
/**
 * Configure a `ResizeObserver` to observe the given `HTMLElement` and update
 * the dimensions whenever it is resized.
 *
 * @param elem - the ref pointing to the `HTMLElement` to observe
 * @param options - the options to pass to the `ResizeObserver`, can be used to
 * pass the initial dimensions.
 */
export default function useResizeObserver(
  elem: Ref<HTMLElement | null>,
  options: Options = {}
) {
  const initialDimensions = {
    width: options.initialWidth || 0,
    height: options.initialHeight || 0,
  }
  const dimens = ref(initialDimensions)
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
