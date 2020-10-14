import FilterBlock from '~/components/Filters/FilterBlock'
import render from '../../test-utils/render'

describe('FilterBlock', () => {
  let options = {}
  let props = null
  beforeEach(() => {
    props = {
      filter: [{ code: 'foo', name: 'bar', checked: false }],
      filterType: 'bar',
    }
    options = { propsData: props }
  })

  it('should render correct contents', () => {
    const wrapper = render(FilterBlock, options)
    expect(wrapper.find('.filter-block').vm).toBeDefined()
  })

  it('should emit filterChanged event', () => {
    const wrapper = render(FilterBlock, options)
    wrapper.vm.onClick()
    expect(wrapper.emitted().filterChanged).toBeTruthy()
  })
})
