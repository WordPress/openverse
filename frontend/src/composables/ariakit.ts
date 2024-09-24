import { computed, onMounted, ref, unref, type MaybeRef } from "vue"
import { useMutationObserver } from "@vueuse/core"

import { addGlobalEventListener } from "@ariakit/core/utils/events"

/**
 * `useSafeLayoutEffect`
 *
 * Strictly speaking, not need for an equivalent.
 *
 * See Vue documentation about watch timing: https://vuejs.org/guide/essentials/watchers.html#callback-flush-timing
 *
 * See this page for a comparison of React's effect lifecycle
 * with Vue's watch: https://gist.github.com/AlexVipond/b3e6c39ab4e1ec7395114210ddcaff92
 *
 * When `canUseDOM` is true, we'll pass `flush: "post"` to the watch options.
 * TODO: How does Vue SSR interact with this?
 */

/**
 * `useInitialValue`
 *
 * Not strictly necessary. Vue `setup` only runs once, so to reference the initial value,
 * either don't use a ref to being with, or use `unref` to remove reactivity.
 *
 * https://vuejs.org/guide/components/props.html#reactive-props-destructure
 */

/**
 * `useLazyValue`
 *
 * ???
 */

/**
 * `useLiveRef`
 *
 * Not necessary. Just use a regular Vue `ref`
 */

/**
 * `usePreviousValue`
 *
 * Potentially unnecessary as `watch` already passes the previous value to the callback
 *
 * `@vueuse/core` `usePrevious` can be used if needed
 */

/**
 * `useEvent`
 *
 * ???
 */

/**
 * `useMergeRefs`
 *
 * Probably not necessary. Instead, components should use `defineExpose`
 * and expose the relevant inner ref.
 */

/**
 * `useId`
 *
 * https://blog.vuejs.org/posts/vue-3-5#useid
 */

/**
 * `useDeferredValue`
 *
 * `@vueuse/core`'s `refDeferred`?
 */

/**
 * `useTagName`
 *
 * Use a computed
 */
export function useTagName(
  element?: MaybeRef<Element | null>,
  type?: MaybeRef<string>
) {
  const tagName = computed(() => {
    return unref(element)?.tagName.toLowerCase() || unref(type)
  })

  return tagName
}

export function useAttribute<T extends HTMLElement>(
  element: MaybeRef<T>,
  attributeName: string,
  defaultValue?: string
) {
  const attribute = ref(defaultValue)

  useMutationObserver(
    element,
    (mutations) => {
      const value =
        (mutations[0]?.target as T | undefined)?.getAttribute(attributeName) ??
        null
      if (value !== null) {
        attribute.value = value
      }
    },
    { attributeFilter: [attributeName] }
  )

  return attribute
}

/**
 * `useUpdateEffect`
 *
 * Use `onMounted`
 */

/**
 * `useUpdateLayoutEffect`
 *
 * Use `onMounted`
 */

/**
 * `useForceUpdate`
 *
 * Use `getCurrentInstance().forceUpdate()`?
 *
 * Otherwise use `:key` with a changeable value...
 */

/**
 * `useBooleanEvent`
 *
 * Depends on usage.
 */

/**
 * `useWrapElement`
 *
 * Depends on usage.
 */

/**
 * `useMetadataProps`
 *
 * Unnecessary in Vue. All props must be declared in Vue
 * and are always separate from attributes passed through
 * to elements. There is never a risk of props being unintentionally
 * leaked into DOM attributes.
 */

export function useIsMouseMoving() {
  onMounted(() => {
    addGlobalEventListener("mousemove", setMouseMoving, true)
    // See https://github.com/ariakit/ariakit/issues/1137
    addGlobalEventListener("mousedown", resetMouseMoving, true)
    addGlobalEventListener("mouseup", resetMouseMoving, true)
    addGlobalEventListener("keydown", resetMouseMoving, true)
    addGlobalEventListener("scroll", resetMouseMoving, true)
  })

  return isMouseMoving
}

/** This ref is used only in `onMounted` calls and so is SSR safe at the top level */
const isMouseMoving = ref(false)
let previousScreenX = 0
let previousScreenY = 0

function hasMouseMovement(event: MouseEvent) {
  const movementX = event.movementX || event.screenX - previousScreenX
  const movementY = event.movementY || event.screenY - previousScreenY
  previousScreenX = event.screenX
  previousScreenY = event.screenY
  return movementX || movementY || process.env.NODE_ENV === "test"
}

function setMouseMoving(event: MouseEvent) {
  if (hasMouseMovement(event)) {
    isMouseMoving.value = true
  }
}

function resetMouseMoving() {
  isMouseMoving.value = false
}
