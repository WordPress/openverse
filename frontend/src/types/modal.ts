import type { Ref } from "vue"

export type ModalVariant =
  | "default"
  | "full"
  | "two-thirds"
  | "fit-content"
  | "centered"
  | "mobile-input"
export type ModalColorMode = "dark" | "light"

export type DialogOptions = {
  autoFocusOnShowRef: Ref<boolean>
  autoFocusOnHideRef: Ref<boolean>
  hideOnClickOutsideRef: Ref<boolean>
  hideOnEscRef: Ref<boolean>
  trapFocusRef: Ref<boolean>
}

export type DialogElements = {
  dialogRef: Ref<HTMLElement | null>
  initialFocusElementRef: Ref<HTMLElement | null>
  triggerElementRef: Ref<HTMLElement | null>
}
