import {
  computed,
  ComputedRef,
  reactive,
  ref,
  Ref,
  SetupContext,
  unref,
  watch,
} from "vue"

import { MaybeRefOrGetter, toValue } from "@vueuse/core"

import { useBodyScrollLock } from "~/composables/use-body-scroll-lock"

type Fn = () => void
export function useDialogControl({
  visibleRef,
  nodeRef,
  lockBodyScroll,
  emit,
  deactivateFocusTrap,
}: {
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
      visible ? lock() : unlock()
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
  const shouldLockBodyScroll = computed(() => unref(lockBodyScroll) ?? false)
  watch(shouldLockBodyScroll, (shouldLock) => {
    if (shouldLock) {
      if (internalVisibleRef.value) {
        lock()
      }
    } else {
      unlock()
    }
  })

  const open = () => (internalVisibleRef.value = true)

  const close = () => {
    const fn = toValue(deactivateFocusTrap)
    if (fn) {
      fn()
    }
    internalVisibleRef.value = false
  }

  const onTriggerClick = () => {
    internalVisibleRef.value = !internalVisibleRef.value
  }

  return {
    close,
    open,
    onTriggerClick,
    triggerA11yProps,
    visible: internalVisibleRef,
  }
}
