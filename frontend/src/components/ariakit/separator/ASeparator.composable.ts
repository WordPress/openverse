import { computed, MaybeRef, unref } from "vue"

export interface SeparatorOptions {
  orientation?: MaybeRef<"horizontal" | "vertical">
}

export function useSeparator({ orientation = "horizontal" }: SeparatorOptions) {
  const attributes = computed(() => ({
    role: "separator",
    "aria-orientation": unref(orientation),
  }))

  return { attributes }
}
