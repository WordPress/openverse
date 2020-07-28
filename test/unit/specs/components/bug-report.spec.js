import BugReport from '@/components/BugReport'
import render from '../../test-utils/render'

describe('BugReport', () => {
  let options = {}
  let dispatchMock = null
  beforeEach(() => {
    dispatchMock = jest.fn()
    options = {
      mocks: {
        $store: {
          dispatch: dispatchMock,
        },
      },
    }
  })

  it('should render correct contents', () => {
    const wrapper = render(BugReport, options)
    expect(wrapper.find('.bug-report').vm).toBeDefined()
  })

  it('should not render required field notice by default', () => {
    const wrapper = render(BugReport, options)
    expect(wrapper.find('.error-message').vm).toBeUndefined()
  })

  it('should render required field notice when fields are empty', () => {
    const wrapper = render(BugReport, options)
    const button = wrapper.find('.submit-form')
    button.trigger('click')
    expect(wrapper.findAll('.error-message').length).toBeGreaterThan(0)
  })

  it('renders thank you when bug reported', () => {
    const props = {
      bugReported: true,
    }
    const wrapper = render(BugReport, { ...options, propsData: props })
    expect(wrapper.find('span').text()).toBe('Thank you!')
  })

  it('does not render thank you when bug not reported', () => {
    const props = {
      bugReported: false,
    }
    const wrapper = render(BugReport, { ...options, propsData: props })
    expect(wrapper.find('span').vm).toBeUndefined()
  })

  it('disabled submit button when reporting bug', () => {
    const props = {
      isReportingBug: true,
    }
    const wrapper = render(BugReport, { ...options, propsData: props })
    expect(wrapper.find('button').attributes('disabled')).toBe('disabled')
  })

  it('enables submit button when not reporting bug', () => {
    const props = {
      isReportingBug: false,
    }
    const wrapper = render(BugReport, { ...options, propsData: props })
    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })

  it('renders error when bug report fails', () => {
    const props = {
      bugReportFailed: true,
    }
    const wrapper = render(BugReport, { ...options, propsData: props })
    expect(wrapper.find('.bug-report-failed').text()).toContain(
      'Please try again'
    )
  })

  it('does not render error when bug report hasnt failed', () => {
    const props = {
      bugReportFailed: false,
    }
    const wrapper = render(BugReport, { ...options, propsData: props })
    expect(wrapper.find('.bug-report-failed').vm).toBeUndefined()
  })
})
