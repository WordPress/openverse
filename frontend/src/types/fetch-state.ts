export interface FetchState {
  isFetching: boolean
  fetchingError: null | string
  hasStarted?: boolean
  isFinished?: boolean
}
