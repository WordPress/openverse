import prepareSearchQueryParams from '~/utils/prepare-search-query-params'

describe('prepareSearchQueryParams', () => {
  it('returns params object clone', () => {
    const params = {
      q: 'foo',
    }

    const result = prepareSearchQueryParams(params)
    expect(result).not.toBe(params) // toBe checks for ref. equality
    expect(result).toEqual(params) // toEqual checks for value equality
  })

  it('swaps "q" key for "creator" key when searchBy equals "creator', () => {
    const params = {
      q: 'foo',
      searchBy: 'creator',
    }

    const result = prepareSearchQueryParams(params)
    expect(result.q).toBeUndefined()
    expect(result.creator).toBe('foo')
  })

  it('swaps "q" key for "tags" key when searchBy equals "tags', () => {
    const params = {
      q: 'foo',
      searchBy: 'tags',
    }

    const result = prepareSearchQueryParams(params)
    expect(result.q).toBeUndefined()
    expect(result.tags).toBe('foo')
  })

  it('doesnt remove q key when searchBy value is empty', () => {
    const params = {
      q: 'foo',
      searchBy: [],
    }

    const result = prepareSearchQueryParams(params)
    expect(result.q).toBe('foo')
  })

  it('removes leading and trailing whitespace from "q" key', () => {
    const params = {
      q: ' foo ',
    }

    const result = prepareSearchQueryParams(params)
    expect(result.q).toBe('foo')
  })
})
