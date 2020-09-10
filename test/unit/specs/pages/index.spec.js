import Homepage from '~/pages/index'
import render from '../../test-utils/render'

describe('Homepage', () => {
  it('should render correct contents', () => {
    const wrapper = render(Homepage)
    expect(wrapper.findComponent({ name: 'hero-section' }).vm).toBeDefined()
  })

  it('commits CLEAR_FILTERS on mounted', () => {
    const options = {
      mocks: {
        $store: {
          commit: jest.fn(),
        },
      },
    }
    render(Homepage, options)

    expect(options.mocks.$store.commit).toHaveBeenCalledWith(
      'CLEAR_FILTERS',
      {}
    )
  })
})
