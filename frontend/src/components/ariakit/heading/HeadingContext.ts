import { provide, inject, type InjectionKey } from "vue"

export type HeadingLevels = 1 | 2 | 3 | 4 | 5 | 6

export type HeadingContext = HeadingLevels
const HeadingContextKey: InjectionKey<HeadingContext> =
  Symbol.for("ariakit-heading")

export const HeadingContext = Object.freeze({
  key: HeadingContextKey,
  provide(context: HeadingContext) {
    provide(HeadingContextKey, context)
  },
  inject() {
    return inject(HeadingContextKey, 0)
  },
})
