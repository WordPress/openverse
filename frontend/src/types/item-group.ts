import type { InjectionKey, Ref } from "vue"

export const itemGroupDirections = [
  "vertical",
  "horizontal",
  "columns",
] as const
export type ItemGroupDirection = typeof itemGroupDirections[number]

export const itemGroupTypes = ["list", "menu", "radiogroup"] as const
export type ItemGroupType = typeof itemGroupTypes[number]

export const itemGroupSizes = ["small", "medium"] as const
export type ItemGroupSize = typeof itemGroupSizes[number]

export type VIemGroupContext = {
  direction: ItemGroupDirection
  bordered: boolean
  type: ItemGroupType
  size: ItemGroupSize
  showCheck: boolean
}

export const VItemGroupContextKey = Symbol(
  "VItemGroupContext"
) as InjectionKey<VIemGroupContext>

export type VIemGroupFocusContext = {
  isGroupFocused: Readonly<Ref<boolean>>
  onItemKeyPress: (event: KeyboardEvent) => void
  selectedCount: Readonly<Ref<number>>
  setSelected: (selected: boolean, previousSelected: boolean) => void
}

export const VItemGroupFocusContextKey = Symbol(
  "VItemGroupFocusContext"
) as InjectionKey<VIemGroupFocusContext>
