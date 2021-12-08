import { ref } from '@nuxtjs/composition-api'
import { getDocument } from 'reakit-utils'

/**
 * Creates a utility for locking body scrolling for a particular node.
 *
 * @param {object} props
 * @param {import('@nuxtjs/composition-api').Ref<HTMLElement>} props.nodeRef
 */
export function useBodyScrollLock({ nodeRef }) {
  const locked = ref(false)
  let scrollY = null

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
    window.scrollTo(0, scrollY)
    scrollY = null
  }

  return { locked, lock, unlock }
}
