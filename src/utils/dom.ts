// Credit: https://github.com/tailwindlabs/headlessui/
import type { ComponentPublicInstance } from '@vue/runtime-dom'
import type { Ref } from '@nuxtjs/composition-api'

export function getDomElement<T extends Element | ComponentPublicInstance>(
  ref?: Ref<T | null>
): T | null {
  if (ref == null) return null
  if (ref.value == null) return null

  return '$el' in ref.value ? (ref.value.$el as T | null) : ref.value
}
