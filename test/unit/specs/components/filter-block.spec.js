import FilterBlock from '~/components/Filters/FilterBlock'
import render from '../../test-utils/render'
import i18n from '../../test-utils/i18n'

describe('FilterBlock', () => {
  let options = {}
  let props = null
  const $t = (key) => i18n.messages[key]
  beforeEach(() => {
    props = {
      filter: [{ code: 'foo', name: 'bar', checked: false }],
      filterType: 'bar',
    }
    options = {
      propsData: props,
      mocks: {
        $t,
      },
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(FilterBlock, options)
    expect(wrapper.find('.filter-block').vm).toBeDefined()
  })

  it('should call filterChanged event', () => {
    const mockMethods = {
      onClick: jest.fn(),
    }
    options.methods = mockMethods
    const wrapper = render(FilterBlock, options)
    const close = wrapper.find('.close')
    expect(close).toBeDefined()

    close.trigger('click')
    expect(options.methods.onClick).toHaveBeenCalled()
  })

  it('should emit filterChanged event', () => {
    const wrapper = render(FilterBlock, options)
    wrapper.vm.onClick()
    expect(wrapper.emitted().filterChanged).toBeTruthy()
  })
})
