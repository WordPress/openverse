import type { ComputedRef, InjectionKey, Ref } from "vue"
import type { ComponentPublicInstance } from "@vue/runtime-dom"

export type TabActivation = "manual" | "auto"
export type TabVariant = "bordered" | "plain"
export type TabsState = {
  // State
  selectedId: Ref<string>

  activation: ComputedRef<TabActivation>
  variant: ComputedRef<TabVariant>

  tabs: Ref<Ref<HTMLElement | ComponentPublicInstance | null>[]>
  panels: Ref<Ref<HTMLElement | null>[]>

  // State mutators
  setSelectedId(id: string): void
  registerTab(tab: Ref<HTMLElement | null>): void
  unregisterTab(tab: Ref<HTMLElement | null>): void
  registerPanel(panel: Ref<HTMLElement | null>): void
  unregisterPanel(panel: Ref<HTMLElement | null>): void
}
export const tabsContextKey = Symbol() as InjectionKey<TabsState>
