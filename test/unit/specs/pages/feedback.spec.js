import FeedbackPage from '~/pages/feedback'
import i18n from '../../../test-utils/i18n'
import render from '../../test-utils/render'

describe('Feedback page', () => {
  it('renders the correct content', () => {
    const $t = (key) => i18n.messages[key]
    const wrapper = render(FeedbackPage, { mocks: { $t } })
    expect(wrapper.find('.feedback-page').element).toBeDefined()
  })
})
