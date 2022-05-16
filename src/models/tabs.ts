import type { ComputedRef, InjectionKey, Ref } from '@nuxtjs/composition-api'
import type { ComponentPublicInstance } from '@vue/runtime-dom'

export type TabsState = {
  // State
  selectedIndex: Ref<number | null>
  initiallySelectedId: string

  activation: ComputedRef<'manual' | 'auto'>
  variant: ComputedRef<'bordered' | 'plain'>

  tabs: Ref<Ref<HTMLElement | ComponentPublicInstance | null>[]>
  panels: Ref<Ref<HTMLElement | null>[]>

  // State mutators
  setSelectedIndex(index: number): void
  registerTab(tab: Ref<HTMLElement | null>): void
  unregisterTab(tab: Ref<HTMLElement | null>): void
  registerPanel(panel: Ref<HTMLElement | null>): void
  unregisterPanel(panel: Ref<HTMLElement | null>): void
}
export const tabsContextKey = Symbol() as InjectionKey<TabsState>
