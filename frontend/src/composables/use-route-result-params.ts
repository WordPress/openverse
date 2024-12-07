import { useRoute } from "#imports"
import { computed } from "vue"

import { getNumber, getString } from "#shared/utils/query-utils"

/**
 * Extracts the media ID, search term, and result position from the single result page route.
 */
export const useRouteResultParams = () => {
  const route = useRoute()

  const resultParams = computed(() => {
    const id = getString(route.params.id)
    const query = getString(route.query.q)
    const position = getNumber(route.query.p)
    return { id, query, position }
  })

  return {
    resultParams,
  }
}
