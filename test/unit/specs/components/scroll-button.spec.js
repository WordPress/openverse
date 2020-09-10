import ScrollButton from '~/components/ScrollButton'
import render from '../../test-utils/render'
import i18n from '../../test-utils/i18n'

describe('Scroll button', () => {
  let props = null
  let options = null
  const $t = (key) => i18n.messages[key]

  beforeEach(() => {
    props = {
      showBtn: false,
    }

    options = {
      propsData: props,
      mocks: {
        $t,
      },
    }
  })

  it('should not be rendered at first', () => {
    const wrapper = render(ScrollButton, options)
    expect(wrapper.find('button').vm).not.toBeDefined()
  })

  it('should be rendered when window scrolls further', () => {
    options.propsData.showBtn = true
    const wrapper = render(ScrollButton, options)
    expect(wrapper.find('button').vm).toBeDefined()
  })

  it('should scroll the window up when clicked', () => {
    const mockMethods = {
      scrollToTop: jest.fn(),
      $t,
    }
    const opts = {
      propsData: {
        ...props,
      },
      methods: mockMethods,
    }
    opts.propsData.showBtn = true
    const wrapper = render(ScrollButton, opts)
    const button = wrapper.find('button')
    expect(button).toBeDefined()
    button.trigger('click')
    expect(mockMethods.scrollToTop).toHaveBeenCalled()
  })
})
