import HelpTooltip from '@/components/HelpTooltip'
import render from '../../test-utils/render'

describe('HelpTooltip', () => {
  it('renders correct content', () => {
    const wrapper = render(HelpTooltip)
    expect(wrapper.find({ name: 'tooltip' }).vm).toBeDefined()
  })
})
