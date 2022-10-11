import { Ref, ref, watch } from '@nuxtjs/composition-api'

import { getDocument } from '~/utils/reakit-utils/dom'

/**
 * Creates a utility for locking body scrolling for a particular node.
 */
export function useBodyScrollLock({
  nodeRef,
  initialLocked = false,
}: {
  nodeRef: Ref<HTMLElement | null>
  initialLocked?: boolean
}) {
  const locked = ref(initialLocked)
  let scrollY: number | null = null

  watch(
    nodeRef,
    (node) => {
      if (node && locked.value) lock()
    },
    {
      immediate: true,
    }
  )
  const lock = () => {
    if (!nodeRef.value) {
      return
    }

    locked.value = true
    const document = getDocument(nodeRef.value)
    scrollY = window.scrollY
    document.body.style.position = 'fixed'
    document.body.style.top = `-${scrollY}px`
  }

  const unlock = () => {
    if (!nodeRef.value) {
      return
    }

    locked.value = false
    const document = getDocument(nodeRef.value)
    document.body.style.position = ''
    document.body.style.top = ''
    if (scrollY) {
      window.scrollTo(0, scrollY)
      scrollY = null
    }
  }

  return { locked, lock, unlock }
}
