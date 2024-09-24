import { computed, MaybeRef, onUnmounted } from "vue"

import { useMemoize } from "@vueuse/core"

import { useTagName } from "~/composables/ariakit"

import type { Renderable } from "~/types/ariakit"

import { HeadingContext } from "./HeadingContext"

export interface UseHeadingOptions {
  templateRef: MaybeRef<Element | null>
  element?: Renderable
}

export function useHeading({ templateRef, element }: UseHeadingOptions) {
  const level = HeadingContext.inject() || 1
  const Element = element || (`h${level}` as const)
  const tagName = useTagName(
    templateRef,
    typeof element === "string" ? element : `h${level}`
  )
  const getIsNativeHeading = useMemoize((tagName: string) =>
    /^h\d$/.test(tagName)
  )
  const isNativeHeading = computed(
    () => !!tagName.value && getIsNativeHeading(tagName.value)
  )
  onUnmounted(() => getIsNativeHeading.clear())

  const attributes = computed(() => ({
    role: !isNativeHeading.value ? "heading" : undefined,
    "aria-level": !isNativeHeading.value ? level : undefined,
  }))

  return {
    Element,
    attributes,
  }
}
