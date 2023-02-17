/**
 * Type utility function for defining `emits` values on components
 * without needing to provide an actual validator function.
 *
 * This works by casting `null` (which acts as a "skip" validation
 * signal) to a function type based on the array of parameters passed
 * in to the function.
 *
 * This is also a way around TS and ESLint rules about unused parameters.
 * The currently recommended way to document emits with Composition API,
 * is to use a function that always returns `true`, so validation is effectively
 * skipped as well. However, then TS and ESlint will complain about unused
 * parameters depending on your configuration. We'd like to keep those rules
 * and compiler flags on as they are useful for catching bugs, but needing to
 * disable them for every emits is cumbersome! Casting null, therefore, is a
 * clean and relatively straightforward solution, at least until we're able
 * to move to the `script setup` syntax and can use `defineEmit`, which solves
 * this problem.
 *
 * @example
 * ```typescript
 * export default defineComponent({
 *  emits: {
 *    click: defineEvent<[MouseEvent]>(), // (e: MouseEvent) => void
 *    open: defineEvent(), // () => void
 *    close: defineEvent<[{ reason: CloseReason }]>(), // (p: { reason: CloseReason }) => void
 *  },
 *  setup(_, { emit }) {
 *    const state = ref('closed')
 *    const handleClick = (e: MouseEvent) => {
 *      // this will cause a TS error if you don't pass a `MouseEvent` payload
 *      emit('click', e)
 *      if (state.value === 'closed') {
 *        emit('open', { reason: 'click' }) // this will cause an error because the `open` event takes no payload
 *      } else {
 *        emit('close') // this will cause an error because the `close` event requires a payload
 *      }
 *    }
 *  }
 * })
 * ```
 */
export function defineEvent<Payload extends unknown[] | null = null>() {
  return null as unknown as Payload extends [...infer A]
    ? (...args: [...A]) => void
    : () => void
}
