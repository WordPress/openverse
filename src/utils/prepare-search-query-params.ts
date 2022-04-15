import type { ApiQueryParams } from '~/utils/search-query-transform'

const NON_API_PARAMS = ['shouldPersistMedia']

export default function prepareSearchQueryParams(
  searchParams: Record<string, string>
): ApiQueryParams {
  const params = {
    ...searchParams,
  }
  NON_API_PARAMS.forEach((key) => delete params[key])

  if (params.q && params.q.length > 0) {
    params.q = params.q.trim()
  }

  // used in search by creator
  // in that case, the creator name will be in `params.q`
  // and params.searchBy will equal "creator"
  // params value after this if block:
  // { q: undefined, creator: "John", searchBy: "creator" }
  if (params.searchBy && params.searchBy.length > 0) {
    params[params.searchBy] = params.q
    delete params.q
  }
  Object.keys(params).forEach((key) => {
    if (params[key] === '') {
      delete params[key]
    }
  })
  return params
}
