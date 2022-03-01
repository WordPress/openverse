import type { DeepReadonly } from '@nuxtjs/composition-api'

/**
 * @see https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze#examples
 */
export function deepFreeze<T>(object: T): DeepReadonly<T> {
  // Retrieve the property names defined on object
  const propNames = Object.getOwnPropertyNames(object)

  // Freeze properties before freezing self

  for (const name of propNames) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore We got the property name from getOwnPropertyNames so this is safe
    const value = object[name]

    if (value && typeof value === 'object') {
      deepFreeze(value)
    }
  }

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore Because the freezing is happening in place TS can't tell we've traversed the tree and frozen the whole object
  return Object.freeze(object)
}
