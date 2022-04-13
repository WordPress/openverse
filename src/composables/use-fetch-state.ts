import { computed, reactive, Ref, ref, watch } from '@nuxtjs/composition-api'

export interface FetchState {
  isFetching: boolean
  fetchingError: null | string
  canFetch?: boolean
  hasStarted?: boolean
  isFinished?: boolean
}
export const initialFetchState: FetchState = {
  hasStarted: false,
  isFetching: false,
  canFetch: true,
  isFinished: false,
  fetchingError: null,
} as const

/* Constants */

/**
 * Mutually exclusive request statuses:
 * - `idle`: the current request has never been sent yet, for example,
 * on the first app load, or after a change in search filters or search term.
 * - `fetching`: the request was sent, but no response was received yet.
 * - `success`: a successful response was received for the current request.
 * - `error`: an error response was received.
 */
const statuses = Object.freeze({
  IDLE: 'idle',
  FETCHING: 'fetching',
  SUCCESS: 'success',
  ERROR: 'error',
} as const)

type Status = typeof statuses[keyof typeof statuses]
/**
 * When one of these statuses is received, the fetchError is set to `null` in a watcher.
 */
const nonErrorStatuses: Status[] = [
  statuses.IDLE,
  statuses.FETCHING,
  statuses.SUCCESS,
]
/**
 * With these statuses, it is possible to send the same request for a new page.
 * This can help debounce requests and prevent racing states.
 */
const canFetchStatuses: Status[] = [statuses.IDLE, statuses.SUCCESS]

/* Composable */
export const useFetchState = (state: FetchState = initialFetchState) => {
  const initialState: {
    status: Status
    fetchError: null | string
    isFinished: boolean
  } = {
    status: statuses.IDLE,
    fetchError: null,
    isFinished: false,
  }
  if (state) {
    if (state.isFetching) {
      initialState.status = statuses.FETCHING
    } else if (state.fetchingError) {
      initialState.status = statuses.ERROR
      initialState.fetchError = state.fetchingError
    } else if (state.hasStarted) {
      initialState.status = statuses.SUCCESS
    }
    if (state.isFinished) {
      initialState.isFinished = true
    }
  }

  const fetchStatus: Ref<Status> = ref(initialState.status)
  const fetchError: Ref<string | null> = ref(initialState.fetchError)
  const isFinished: Ref<boolean> = ref(initialState.isFinished)

  watch(fetchStatus, () => {
    if (nonErrorStatuses.includes(fetchStatus.value)) {
      fetchError.value = null
    }
  })
  const reset = () => {
    fetchStatus.value = statuses.IDLE
    fetchError.value = null
    isFinished.value = false
  }
  const startFetching = () => {
    fetchStatus.value = statuses.FETCHING
  }
  /**
   * Called when any response is received. For an error response,
   * pass the errorMessage string as a parameter.
   * @param errorMessage - the message to show for response error.
   */
  const endFetching = (errorMessage?: string) => {
    if (errorMessage) {
      fetchStatus.value = statuses.ERROR
      fetchError.value = errorMessage
      isFinished.value = true
    } else {
      fetchStatus.value = statuses.SUCCESS
    }
  }
  /**
   * Used for paginated requests, `isFinished` means there are no more pages left.
   * It does not change the fetchStatus, which should be handled separately.
   */
  const setFinished = () => {
    isFinished.value = true
  }

  /**
   * Whether the current request has been sent. This can be useful for displaying
   * initial search page with a blank search term, such as for a provider search page.
   */
  const hasStarted = computed(() => fetchStatus.value !== statuses.IDLE)
  const isFetching = computed(() => fetchStatus.value === statuses.FETCHING)
  /**
   * Whether a new request for the same parameters with a new page can be sent.
   * Use this to ensure that prevent racing requests.
   */
  const canFetch = computed(
    () => canFetchStatuses.includes(fetchStatus.value) && !isFinished.value
  )
  const fetchingError = computed(() => fetchError.value)

  const fetchState: FetchState = reactive({
    hasStarted,
    isFetching,
    canFetch,
    isFinished,
    fetchingError,
  })

  return {
    fetchState,

    startFetching,
    endFetching,
    setFinished,
    reset,
  }
}

export const updateFetchState = (
  initial: FetchState,
  action: 'end' | 'finish' | 'start' | 'reset',
  option?: string
) => {
  const fetchState = useFetchState(initial)
  switch (action) {
    case 'end':
      fetchState.endFetching(option)
      break
    case 'start':
      fetchState.startFetching()
      break
    case 'finish':
      fetchState.setFinished()
      break
    case 'reset':
      fetchState.reset()
      break
  }
  return fetchState.fetchState
}
