import FilterDisplay from '~/components/Filters/FilterDisplay'
import render from '../../test-utils/render'

describe('FilterDisplay', () => {
  let options = null
  let filters = null

  beforeEach(() => {
    filters = {
      licenses: [{ code: 'foo', name: 'bar', checked: false }],
      licenseTypes: [{ code: 'foo', name: 'bar', checked: false }],
      categories: [{ code: 'foo', name: 'bar', checked: false }],
      extensions: [{ code: 'foo', name: 'bar', checked: false }],
      aspectRatios: [{ code: 'foo', name: 'bar', checked: false }],
      sizes: [{ code: 'foo', name: 'bar', checked: false }],
      providers: [{ code: 'foo', name: 'bar', checked: false }],
      searchBy: { creator: false },
    }
    options = {
      propsData: {
        query: {
          license: 'cc0',
          license_type: 'foo',
          categories: 'foo',
          extension: 'foo',
          aspect_ratio: 'foo',
          size: 'foo',
          source: 'foo',
        },
      },
      mocks: {
        $store: {
          state: {
            query: {
              q: 'foo',
              provider: 'foo',
            },
            filters,
          },
          dispatch: jest.fn(),
        },
      },
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(FilterDisplay, options)
    expect(wrapper.find('.filter-display'))
  })

  it('should render filter if checked', () => {
    filters.licenses[0].checked = true
    const wrapper = render(FilterDisplay, options)
    expect(wrapper.find({ name: 'FilterBlock' }).vm).toBeDefined()
  })

  it('should render filter by caption label', () => {
    options.mocks.$store.state.isFilterApplied = true
    const wrapper = render(FilterDisplay, options)
    expect(wrapper.find('.caption').element.textContent).toBe('Filter By')
  })
})
