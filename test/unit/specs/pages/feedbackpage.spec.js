import FeedbackPage from '@/pages/FeedbackPage'
import render from '../../test-utils/render'

describe('Feedback page', () => {
  it('renders the correct content', () => {
    const wrapper = render(FeedbackPage)
    expect(wrapper.find({ name: 'header-section' }).vm).toBeDefined()
    expect(wrapper.find({ name: 'footer-section' }).vm).toBeDefined()
    expect(wrapper.find('.feedback-page').element).toBeDefined()
  })
})
