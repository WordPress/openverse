import { useFocusOnShow } from '~/composables/use-focus-on-show'
import { useFocusOnHide } from '~/composables/use-focus-on-hide'
import { useHideOnClickOutside } from '~/composables/use-hide-on-click-outside'
import { useFocusOnBlur } from '~/composables/use-focus-on-blur'
import { usePopper } from '~/composables/use-popper'

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} popoverRef
 * @property {import('./types').ToRefs<import('../components/VPopover/VPopoverContent.types').Props>} popoverPropsRefs
 */

/**
 * @param {Props} props
 */
export function usePopoverContent(props) {
  const focusOnBlur = useFocusOnBlur(props)
  useFocusOnShow(props)
  useFocusOnHide(props)
  useHideOnClickOutside(props)
  usePopper(props)

  return { focusOnBlur }
}
