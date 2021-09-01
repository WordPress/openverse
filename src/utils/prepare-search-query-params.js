export default function prepareSearchQueryParams(searchParams) {
  const params = {
    ...searchParams,
  }

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

  return params
}
