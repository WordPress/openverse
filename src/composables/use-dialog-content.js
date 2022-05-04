import { useFocusOnShow } from '~/composables/use-focus-on-show'
import { useFocusOnHide } from '~/composables/use-focus-on-hide'
import { useHideOnClickOutside } from '~/composables/use-hide-on-click-outside'
import { useFocusOnBlur } from '~/composables/use-focus-on-blur'

/**
 * @typedef InnerProps
 * @property {HTMLElement} dialogRef
 * @property {boolean} visibleRef
 * @property {boolean} autoFocusOnShowRef
 * @property {HTMLElement} triggerElementRef
 * @property {boolean} autoFocusOnHideRef
 * @property {boolean} hideOnClickOutsideRef
 * @property {boolean} hideOnEscRef
 * @property {HTMLElement} initialFocusElementRef
 * @property {() => void} hideRef
 */

/** @typedef {import('./types').ToRefs<InnerProps> & { emit: import('@nuxtjs/composition-api').SetupContext['emit']}} Props */

/**
 * @param {Props} params
 */
export function useDialogContent({ emit, ...props }) {
  const focusOnBlur = useFocusOnBlur(props)
  useFocusOnShow(props)
  useFocusOnHide(props)
  useHideOnClickOutside(props)

  /**
   * @param {KeyboardEvent} event
   */
  const onKeyDown = (event) => {
    emit('keydown', event)

    if (event.defaultPrevented) return
    if (event.key !== 'Escape') return
    if (!props.hideOnEscRef.value) return

    event.stopPropagation()
    props.hideRef.value()
  }

  /**
   * @param {FocusEvent} event
   */
  const onBlur = (event) => {
    emit('blur', event)
    focusOnBlur(event)
  }

  return { onKeyDown, onBlur }
}
