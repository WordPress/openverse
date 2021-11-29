import ScrollButton from '~/components/ScrollButton'
import render from '../../test-utils/render'

describe('Scroll button', () => {
  let props = null
  let options = null

  beforeEach(() => {
    props = {
      showBtn: false,
    }
    options = { propsData: props }
  })

  it('should not be rendered at first', () => {
    const wrapper = render(ScrollButton, options)
    expect(wrapper.find('button').vm).not.toBeDefined()
  })

  it('should be rendered when window scrolls further', () => {
    options.propsData.showBtn = true
    const scrollBtn = render(ScrollButton, options).find('button')
    expect(scrollBtn).toBeDefined()
    expect(scrollBtn.isVisible()).toBe(true)
  })
})
