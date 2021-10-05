import ContentReportForm from '~/components/ContentReport/ContentReportForm'
import render from '../../../test-utils/render'
import i18n from '../../../test-utils/i18n'
import { PROVIDER, REPORT_CONTENT } from '~/constants/store-modules'
import { SEND_CONTENT_REPORT } from '~/constants/action-types'
import { REPORT_FORM_CLOSED } from '~/constants/mutation-types'

describe('ContentReportForm', () => {
  let props = null
  let options = {}
  let storeState = null
  let dispatchMock = null
  let commitMock = null
  const $t = (key) => i18n.messages[key]
  beforeEach(() => {
    props = {
      image: { id: 1, url: 'http://foo.bar' },
    }

    dispatchMock = jest.fn()
    commitMock = jest.fn()

    storeState = {
      $store: {
        dispatch: dispatchMock,
        commit: commitMock,
        state: {
          [PROVIDER]: {
            imageProviders: [],
          },
          [REPORT_CONTENT]: {
            isReportSent: false,
            reportFailed: false,
          },
        },
      },
    }

    options = {
      propsData: props,
      mocks: {
        ...storeState,
        $t,
      },
    }
  })

  it('should contain the correct contents', async () => {
    const wrapper = render(ContentReportForm, options)
    expect(wrapper.find('.arrow-popup').element).toBeDefined()
  })

  it('should render report sent', async () => {
    storeState.$store.state[REPORT_CONTENT].isReportSent = true
    const wrapper = render(ContentReportForm, options)
    expect(wrapper.findComponent({ name: 'DoneMessage' }).vm).toBeDefined()
  })

  it('should render error message', async () => {
    storeState.$store.state[REPORT_CONTENT].reportFailed = true
    const wrapper = render(ContentReportForm, options)
    expect(wrapper.findComponent({ name: 'ReportError' }).vm).toBeDefined()
  })

  it('should render dmca notice', async () => {
    const wrapper = render(ContentReportForm, options)
    await wrapper.setData({ selectedCopyright: true })
    expect(wrapper.findComponent({ name: 'DmcaNotice' }).vm).toBeDefined()
  })

  it('should render other type form', async () => {
    const wrapper = render(ContentReportForm, options)
    await wrapper.setData({ selectedOther: true })
    expect(wrapper.findComponent({ name: 'OtherIssueForm' }).vm).toBeDefined()
  })

  it('should navigate to other form', async () => {
    const wrapper = render(ContentReportForm, options)
    const radio = wrapper.find('#other')
    await radio.setChecked()

    const button = wrapper.find('.next-button')
    await button.trigger('click')
    expect(wrapper.findComponent({ name: 'OtherIssueForm' }).vm).toBeDefined()
  })

  it('should dispatch SEND_CONTENT_REPORT on next when mature is selected', async () => {
    const wrapper = render(ContentReportForm, options)
    const radio = wrapper.find('#mature')
    await radio.setChecked()

    const button = wrapper.find('.next-button')
    await button.trigger('click')
    expect(dispatchMock).toHaveBeenCalledWith(
      `${REPORT_CONTENT}/${SEND_CONTENT_REPORT}`,
      {
        identifier: props.image.id,
        reason: 'mature',
        description: '',
      }
    )
  })

  it('should not dispatch SEND_CONTENT_REPORT on next when dmca is selected', async () => {
    const wrapper = render(ContentReportForm, options)
    const radio = wrapper.find('#dmca')
    await radio.setChecked()

    const button = wrapper.find('.next-button')
    await button.trigger('click')
    expect(dispatchMock).not.toHaveBeenCalled()
  })

  it('should dispatch SEND_CONTENT_REPORT on other form submit', async () => {
    const wrapper = render(ContentReportForm, options)
    await wrapper.setData({ selectedReason: 'other' })
    const description = 'foo bar'
    wrapper.vm.sendContentReport(description)
    expect(dispatchMock).toHaveBeenCalledWith(
      `${REPORT_CONTENT}/${SEND_CONTENT_REPORT}`,
      {
        identifier: props.image.id,
        reason: 'other',
        description,
      }
    )
  })

  it('should close form', async () => {
    const wrapper = render(ContentReportForm, options)

    const button = wrapper.find('.close-button')
    await button.trigger('click')
    expect(commitMock).toHaveBeenCalledWith(
      `${REPORT_CONTENT}/${REPORT_FORM_CLOSED}`
    )
  })
})
