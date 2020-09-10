import FilterChecklist from '~/components/Filters/FilterChecklist'
import render from '../../test-utils/render'
import i18n from '../../test-utils/i18n'

describe('FilterChecklist', () => {
  let options = {}
  let props = null
  const $t = (key) => i18n.messages[key]
  const eventData = {
    target: {
      id: 'foo',
    },
  }

  beforeEach(() => {
    props = {
      options: [{ code: 'foo', name: 'bar', checked: false }],
      title: 'Foo',
      filterType: 'bar',
      disabled: false,
    }
    options = {
      propsData: props,
      mocks: {
        $store: {
          state: {
            experiments: [
              {
                name: 'filter_expansion',
                case: 'filters_collapsed',
              },
            ],
          },
        },
        $t,
      },
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(FilterChecklist, options)
    expect(wrapper.find('.filters').vm).toBeDefined()
  })

  it('should render filter visibility toggle button', () => {
    const wrapper = render(FilterChecklist, options)
    expect(wrapper.find('.filter-visibility-toggle').element).toBeDefined()
  })

  it('visibility toggle button should be in collapsed state by default', () => {
    const wrapper = render(FilterChecklist, options)
    expect(wrapper.find('.angle-down').element).toBeDefined()
  })

  it('hides checklist when visibility toggle button pressed twice', () => {
    const wrapper = render(FilterChecklist, options)
    wrapper.find('.filter-visibility-toggle').trigger('click') // should open
    wrapper.find('.filter-visibility-toggle').trigger('click') // should close
    expect(wrapper.find('.angle-down').element).toBeDefined()
  })

  it('should call filterChanged event', () => {
    const mockMethods = {
      onValueChange: jest.fn(),
    }
    options.methods = mockMethods

    const wrapper = render(FilterChecklist, options)
    wrapper.setData({ filtersVisible: true })

    const checkbox = wrapper.find('.filter-checkbox')
    expect(checkbox.element).toBeDefined()

    checkbox.trigger('change')
    expect(options.methods.onValueChange).toHaveBeenCalled()
  })

  it('should emit filterChanged event', () => {
    const wrapper = render(FilterChecklist, options)
    wrapper.vm.onValueChange(eventData)
    expect(wrapper.emitted().filterChanged).toBeTruthy()
  })
})
