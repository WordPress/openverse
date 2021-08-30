import FilterTag from '~/components/Filters/FilterTag'
import render from '../../test-utils/render'

describe('FilterTag', () => {
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
    const wrapper = render(FilterTag, options)
    expect(wrapper.find('.filter-block').vm).toBeDefined()
  })

  it('should emit filterChanged event', () => {
    const wrapper = render(FilterTag, options)
    wrapper.vm.onClick()
    expect(wrapper.emitted().filterChanged).toBeTruthy()
  })
})
