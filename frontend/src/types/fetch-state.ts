import type { NuxtError } from "@nuxt/types"

export interface BaseFetchState {
  isFetching: boolean
  hasStarted?: boolean
  isFinished?: boolean
}

export interface FetchState extends BaseFetchState {
  fetchingError: null | string
}

/**
 * The fetching error has the props required for Nuxt's
 * error page.
 * TODO: replace FetchState with FetchStateWithNuxtError
 * in the provider, main media and related media stores.
 */
export interface FetchStateWithNuxtError extends BaseFetchState {
  fetchingError: null | NuxtError
}
