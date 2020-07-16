import Tooltip from '@/components/Tooltip'
import render from '../../test-utils/render'

const Foo = {
  name: 'foo-component',
  template: '<p>foo</p>',
}

describe('Tooltip', () => {
  it('should render children component', () => {
    const wrapper = render(Tooltip, {
      slots: {
        default: [Foo],
      },
    })
    expect(wrapper.find('p').vm).toBeDefined()
  })

  it('should render tooltip on click', () => {
    const wrapper = render(Tooltip, {
      slots: {
        default: [Foo],
      },
      propsData: {
        tooltip: 'Foo Bar',
      },
    })

    const div = wrapper.find('div')
    div.trigger('click')
    expect(wrapper.find('.help-tooltip').vm).toBeDefined()
  })

  it('should hide tooltip on click', () => {
    const wrapper = render(Tooltip, {
      slots: {
        default: [Foo],
      },
      propsData: {
        tooltip: 'Foo Bar',
      },
    })

    const div = wrapper.find('div')
    div.trigger('click')

    const tooltip = wrapper.find('.help-tooltip')
    tooltip.trigger('click')
    expect(wrapper.find('.help-tooltip').vm).toBeUndefined()
  })
})
