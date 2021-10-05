import Dropdown from '~/components/Dropdown'
import render from '../../test-utils/render'

describe('Dropdown', () => {
  let options = {}
  let props = null
  beforeEach(() => {
    props = {
      filter: [{ text: 'Code is Poetry' }],
      filterType: 'bar',
      text: 'Dropdown',
    }
    options = {
      propsData: props,
      scopedSlots: {
        default: `<a id="dropdown-item" @focus="props.onFocus()">WordPress.org</a>`,
      },
    }
  })

  it('should visually hide the dropdown when not focused', () => {
    const wrapper = render(Dropdown, options)
    const dropdownWrapper = wrapper.get('[role="menu"]')
    expect(dropdownWrapper.classes()).not.toContain('visible')
  })

  it('should be visible when the container is focused', async () => {
    const wrapper = render(Dropdown, options)
    await wrapper.trigger('focus')
    const dropdownWrapper = wrapper.get('[role="menu"]')
    expect(dropdownWrapper.classes()).toContain('visible')
  })

  it('should be visible when the dropdown items are focused', async () => {
    const wrapper = render(Dropdown, options)
    const dropdownItem = wrapper.get('#dropdown-item')
    await dropdownItem.trigger('focus')
    const dropdownWrapper = wrapper.get('[role="menu"]')
    expect(dropdownWrapper.classes()).toContain('visible')
  })
})
