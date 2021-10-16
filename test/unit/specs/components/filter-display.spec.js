import { render } from '@testing-library/vue'

import FilterDisplay from '~/components/Filters/FilterDisplay'

describe('FilterDisplay', () => {
  const options = {
    mocks: {
      $store: {
        state: {
          query: {
            q: 'foo',
            provider: 'foo',
          },
          filters: {},
        },
        dispatch: jest.fn(),
        getters: {
          isAnyFilterApplied: true,
          appliedFilterTags: [
            {
              code: 'cc0',
              filterType: 'license',
              name: 'filters.licenses.cc0',
            },
          ],
        },
      },
    },
  }

  it('should render correct contents', () => {
    const { container } = render(FilterDisplay, options)
    expect(container.firstChild).toMatchSnapshot()
  })
})
