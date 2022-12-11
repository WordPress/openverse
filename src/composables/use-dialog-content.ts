import { useFocusOnShow } from '~/composables/use-focus-on-show'
import { useFocusOnHide } from '~/composables/use-focus-on-hide'
import { useHideOnClickOutside } from '~/composables/use-hide-on-click-outside'
import { useFocusOnBlur } from '~/composables/use-focus-on-blur'

import type { Ref } from '@nuxtjs/composition-api'
import type { SetupContext } from 'vue'

type Props = {
  dialogRef: Ref<HTMLElement | null>
  visibleRef: Ref<boolean>
  autoFocusOnShowRef: Ref<boolean>
  autoFocusOnHideRef: Ref<boolean>
  trapFocusRef: Ref<boolean>
  triggerElementRef: Ref<HTMLElement | null>
  hideOnClickOutsideRef: Ref<boolean>
  hideOnEscRef: Ref<boolean>
  initialFocusElementRef?: Ref<HTMLElement | null>
  hideRef: Ref<() => void>
  emit: SetupContext['emit']
}

export function useDialogContent({ emit, ...props }: Props) {
  const focusOnBlur = useFocusOnBlur({
    dialogRef: props.dialogRef,
    visibleRef: props.visibleRef,
  })
  useFocusOnShow(props)
  useFocusOnHide({
    dialogRef: props.dialogRef,
    triggerElementRef: props.triggerElementRef,
    visibleRef: props.visibleRef,
    autoFocusOnHideRef: props.autoFocusOnHideRef,
  })
  useHideOnClickOutside({
    dialogRef: props.dialogRef,
    visibleRef: props.visibleRef,
    hideOnClickOutsideRef: props.hideOnClickOutsideRef,
    triggerElementRef: props.triggerElementRef,
    hideRef: props.hideRef,
  })

  const onKeyDown = (event: KeyboardEvent) => {
    emit('keydown', event)

    if (event.defaultPrevented) return
    if (event.key !== 'Escape') return
    if (!props.hideOnEscRef.value) return

    event.stopPropagation()
    props.hideRef.value()
  }

  const onBlur = (event: FocusEvent) => {
    emit('blur', event)
    focusOnBlur(event)
  }

  return { onKeyDown, onBlur }
}
