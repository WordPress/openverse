import {
  computed,
  ComputedRef,
  reactive,
  ref,
  Ref,
  SetupContext,
  unref,
  watch,
} from "@nuxtjs/composition-api"

import { useBodyScrollLock } from "~/composables/use-body-scroll-lock"

export function useDialogControl({
  visibleRef,
  nodeRef,
  lockBodyScroll,
  emit,
}: {
  visibleRef?: Ref<boolean>
  nodeRef?: Ref<HTMLElement | null>
  lockBodyScroll?: ComputedRef<boolean> | boolean
  emit: SetupContext["emit"]
}) {
  const internallyControlled = typeof visibleRef === "undefined"
  const internalVisibleRef = internallyControlled ? ref(false) : visibleRef

  const triggerA11yProps = reactive({
    "aria-expanded": false,
    "aria-haspopup": "dialog",
  })

  watch(internalVisibleRef, (visible) => {
    triggerA11yProps["aria-expanded"] = visible
    if (shouldLockBodyScroll.value) {
      visible ? lock() : unlock()
    }
    if (!internallyControlled) emit(visible ? "open" : "close")
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
  const shouldLockBodyScroll = computed(() => unref(lockBodyScroll) ?? true)
  watch(shouldLockBodyScroll, (shouldLock) => {
    shouldLock ? lock() : unlock()
  })

  const open = () => (internalVisibleRef.value = true)

  const close = () => (internalVisibleRef.value = false)

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
