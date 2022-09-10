import { getCurrentScope, onScopeDispose } from '@nuxtjs/composition-api'

export function tryOnScopeDispose(fn: () => void) {
  if (getCurrentScope()) {
    onScopeDispose(fn)
    return true
  } else {
    return false
  }
}
