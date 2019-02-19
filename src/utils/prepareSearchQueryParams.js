export default function prepareSearchQueryParams(searchParams) {
  const params = {
    ...searchParams,
  };

  if (params.searchBy && params.searchBy.length > 0) {
    params[params.searchBy] = params.q;
    delete params.q;
  }

  return params;
}
