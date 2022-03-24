import { computed, reactive, Ref, ref, watch } from '@nuxtjs/composition-api'

export interface FetchState {
  isFetching: boolean
  fetchingError: null | string
  canFetch?: boolean
  hasStarted?: boolean
  isFinished?: boolean
}

/* Constants */

/**
 * Statuses of requests:
 * - `idle`: the current request has never been sent yet, for example,
 * on the first app load, or after a change in search filters or search term.
 * - `fetching`: the request was sent, but no response was received yet.
 * - `success`: a successful response was received for the current request.
 * - `finished`: for multi-page requests, this is true when no more pages are left.
 * - `error`: an error response was received.
 */
const statuses = Object.freeze({
  IDLE: 'idle',
  FETCHING: 'fetching',
  SUCCESS: 'success',
  ERROR: 'error',
  FINISHED: 'finished',
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

export const useFetchState = (initialState = statuses.IDLE) => {
  const fetchStatus: Ref<Status> = ref(initialState)
  const fetchError: Ref<string | null> = ref(null)

  watch(fetchStatus, () => {
    if (nonErrorStatuses.includes(fetchStatus.value)) {
      fetchError.value = null
    }
  })
  const reset = () => {
    fetchStatus.value = statuses.IDLE
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
    } else {
      fetchStatus.value = statuses.SUCCESS
    }
  }
  const setFinished = () => {
    fetchStatus.value = statuses.FINISHED
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
  const canFetch = computed(() => canFetchStatuses.includes(fetchStatus.value))
  /**
   * Used for paginated requests, `isFinished` means there are no more pages left.
   */
  const isFinished = computed(() => fetchStatus.value === statuses.FINISHED)
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
