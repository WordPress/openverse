import { isClient } from '~/constants/window'

import type { StateTree } from 'pinia'

/**
 * On the server, set the state to `initialState`.
 * On the client, reuse the server state that is saved as a property on `window.$nuxt.context`
 */
export function initializeState<T>(storeId: string, initialState: T) {
  if (!isClient) {
    return initialState
  }
  const serverState = window?.$nuxt?.context?.$pinia?.state?.value

  return serverState &&
    serverState[storeId] &&
    Object.keys(serverState[storeId]).length > 0
    ? (JSON.parse(JSON.stringify(serverState[storeId].state)) as T)
    : initialState
}

/**
 * Check if the state in `window.$nuxt` contains a reactive value `refName` inside the `storeId` store.
 * @param serverState - the state object from `window.$nuxt`. Is null on the server.
 * @param storeId - the id of the store the refName is in.
 * @param refName - the name of a reactive store property to find.
 */
const serverStateHasRef = (
  serverState: Record<string, StateTree> | null,
  storeId: string,
  refName: string
) => {
  return Boolean(
    serverState &&
      serverState[storeId] &&
      Object.keys(serverState[storeId]).length > 0 &&
      refName in serverState[storeId]
  )
}

/**
 * Use this to hydrate the state if it's a collection of `ref`s or `reactive`s
 * instead of a single reactive `state` value.
 * @param storeId - the id of the store
 * @param refName - name of the state ref or reactive value
 * @param initialRef - initial value of the ref/reactive to be used if no value is available in the `nuxt.context`
 */
export function initializeStateRef<T>(
  storeId: string,
  refName: string,
  initialRef: T
) {
  if (!isClient) {
    return initialRef
  }
  const serverState = window?.$nuxt?.context?.$pinia?.state?.value
  return serverStateHasRef(serverState, storeId, refName)
    ? (JSON.parse(JSON.stringify(serverState[storeId][refName])) as T)
    : initialRef
}
