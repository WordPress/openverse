import {
  computed,
  ComputedRef,
  reactive,
  ref,
  Ref,
  SetupContext,
  watch,
} from "vue"

import { MaybeRefOrGetter, toValue } from "@vueuse/core"

import { useBodyScrollLock } from "~/composables/use-body-scroll-lock"
import { useDialogStack } from "~/composables/use-dialog-stack"

type Fn = () => void
export function useDialogControl({
  id,
  visibleRef,
  nodeRef,
  lockBodyScroll,
  emit,
  deactivateFocusTrap,
}: {
  id: MaybeRefOrGetter<string | undefined>
  visibleRef?: Ref<boolean>
  nodeRef?: Ref<HTMLElement | null>
  lockBodyScroll?: ComputedRef<boolean> | boolean
  emit: SetupContext["emit"]
  deactivateFocusTrap?: MaybeRefOrGetter<Fn | undefined>
}) {
  const internallyControlled = typeof visibleRef === "undefined"
  const internalVisibleRef = internallyControlled ? ref(false) : visibleRef

  const triggerA11yProps = reactive({
    "aria-expanded": false,
    "aria-haspopup": "dialog",
  })

  watch(internalVisibleRef, (visible, _, onCleanup) => {
    triggerA11yProps["aria-expanded"] = visible
    if (shouldLockBodyScroll.value) {
      if (visible) {
        lock()
      } else {
        unlock()
      }
    }
    emit(visible ? "open" : "close")
    onCleanup(() => {
      if (shouldLockBodyScroll.value) {
        unlock()
      }
    })
  })

  let lock = () => {
      /** */
    },
    unlock = () => {
      /** */
    }
  if (nodeRef) {
    const bodyScroll = useBodyScrollLock({ nodeRef })
    lock = bodyScroll.lock
    unlock = bodyScroll.unlock
  }
  const shouldLockBodyScroll = computed(() => toValue(lockBodyScroll) ?? false)
  watch(shouldLockBodyScroll, (shouldLock) => {
    if (shouldLock) {
      if (internalVisibleRef.value) {
        lock()
      }
    } else {
      unlock()
    }
  })

  const open = () => {
    internalVisibleRef.value = true
    pushModalToStack()
  }

  const close = () => {
    popModalFromStack()
    const fn = toValue(deactivateFocusTrap)
    if (fn) {
      fn()
    }
    internalVisibleRef.value = false
  }

  const pushModalToStack = () => {
    const { push } = useDialogStack()
    const idValue = toValue(id)
    if (idValue) {
      push(idValue)
    }
  }

  const popModalFromStack = () => {
    const openModalStack = useDialogStack()
    const idValue = toValue(id)
    if (idValue && openModalStack.indexOf(idValue) > -1) {
      openModalStack.pop()
    }
  }

  const onTriggerClick = () => {
    if (internalVisibleRef.value) {
      close()
    } else {
      open()
    }
  }

  return {
    close,
    open,
    onTriggerClick,
    triggerA11yProps,
    visible: internalVisibleRef,
  }
}
