import AboutPage from '~/pages/about'
import render from '../../test-utils/render'

describe('AboutPage', () => {
  it('should render correct contents', () => {
    const wrapper = render(AboutPage)

    expect(wrapper.find('.table').element).toBeDefined()
  })
})
