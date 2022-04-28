import { Ref, ref } from '@nuxtjs/composition-api'

import { getDocument } from '~/utils/dom/get-document'

/**
 * Creates a utility for locking body scrolling for a particular node.
 */
export function useBodyScrollLock({ nodeRef }: { nodeRef: Ref<HTMLElement> }) {
  const locked = ref(false)
  let scrollY: number | null = null

  const lock = () => {
    if (!nodeRef.value) {
      throw new Error(
        'useBodyScrollLock: Cannot lock body with undefined node reference'
      )
    }

    locked.value = true
    const document = getDocument(nodeRef.value)
    scrollY = window.scrollY
    document.body.style.position = 'fixed'
    document.body.style.top = `-${scrollY}px`
  }

  const unlock = () => {
    if (!nodeRef.value) {
      throw new Error(
        'useBodyScrollLock: Cannot unlock body with undefined node reference'
      )
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
