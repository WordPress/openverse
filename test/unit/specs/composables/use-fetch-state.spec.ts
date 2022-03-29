import { useFetchState } from '~/composables/use-fetch-state'

describe('useFetchState', () => {
  it('should use the default values', () => {
    const fetchState = useFetchState()
    expect(fetchState.fetchState).toEqual({
      isFetching: false,
      isFinished: false,
      fetchingError: null,
      canFetch: true,
      hasStarted: false,
    })
  })
  it('should start fetching', () => {
    const fetchState = useFetchState()
    fetchState.startFetching()

    expect(fetchState.fetchState).toEqual({
      isFetching: true,
      isFinished: false,
      fetchingError: null,
      canFetch: false,
      hasStarted: true,
    })
  })
  it('should end fetching with success', () => {
    const fetchState = useFetchState()
    fetchState.endFetching()
    expect(fetchState.fetchState).toEqual({
      isFetching: false,
      isFinished: false,
      fetchingError: null,
      canFetch: true,
      hasStarted: true,
    })
  })
  it('should end fetching with error', () => {
    const fetchState = useFetchState()
    fetchState.endFetching('Server Error')
    expect(fetchState.fetchState).toEqual({
      isFetching: false,
      isFinished: true,
      fetchingError: 'Server Error',
      canFetch: false,
      hasStarted: true,
    })
  })
  it('setFinished should set isFinished to true, and isFetching to false', () => {
    const fetchState = useFetchState()
    fetchState.startFetching()
    fetchState.endFetching()
    fetchState.setFinished()
    expect(fetchState.fetchState).toEqual({
      isFetching: false,
      isFinished: true,
      fetchingError: null,
      canFetch: false,
      hasStarted: true,
    })
  })
})
