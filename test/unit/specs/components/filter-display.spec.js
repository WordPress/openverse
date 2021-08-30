import render from '../../test-utils/render'
import FilterDisplay from '~/components/Filters/FilterDisplay'
import FilterTag from '~/components/Filters/FilterTag'

describe('FilterDisplay', () => {
  let options = null
  let filters = null

  beforeEach(() => {
    filters = {
      licenses: [{ code: 'fooLicense', name: 'bar', checked: false }],
      licenseTypes: [{ code: 'fooType', name: 'bar', checked: false }],
      categories: [{ code: 'fooCategory', name: 'bar', checked: false }],
      extensions: [{ code: 'fooExtension', name: 'bar', checked: false }],
      aspectRatios: [{ code: 'fooRatio', name: 'bar', checked: false }],
      sizes: [{ code: 'fooSize', name: 'bar', checked: false }],
      providers: [{ code: 'fooProvider', name: 'bar', checked: false }],
      searchBy: { creator: false },
    }
    options = {
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
  })

  it('should render correct contents', () => {
    const wrapper = render(FilterDisplay, options)
    expect(wrapper.find('.filter-display'))
  })

  it('should render filter if checked', () => {
    filters.licenses[0].checked = true
    const wrapper = render(FilterDisplay, options)
    expect(wrapper.findComponent(FilterTag).vm).toBeDefined()
  })

  it('should render filter by caption label', () => {
    const wrapper = render(FilterDisplay, options)
    expect(wrapper.find('.caption').element.textContent.trim()).toBe(
      'filters.filter-by'
    )
  })
})
