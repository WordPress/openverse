export interface BaseFetchState {
  isFetching: boolean
  hasStarted?: boolean
  isFinished?: boolean
}

export interface FetchState<ErrorType = string> extends BaseFetchState {
  fetchingError: null | ErrorType
}
