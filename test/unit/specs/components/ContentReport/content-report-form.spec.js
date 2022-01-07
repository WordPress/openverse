import { fireEvent, render, screen } from '@testing-library/vue'
import { createLocalVue } from '@vue/test-utils'
import VueI18n from 'vue-i18n'
import VContentReportForm from '~/components/VContentReport/VContentReportForm.vue'

const messages = require('~/locales/en.json')
const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages,
})

const getCloseButton = () =>
  screen.getByRole('button', {
    name: /close-form/i,
  })
const getNextButton = () =>
  screen.getByRole('button', {
    name: /next/i,
  })
const getDmcaInput = () =>
  screen.getByRole('radio', {
    name: /dmca/i,
  })
const getMatureInput = () =>
  screen.getByRole('radio', {
    name: /mature/i,
  })
const getOtherInput = () =>
  screen.getByRole('radio', {
    name: /other/i,
  })

describe('VContentReportForm', () => {
  let props = null
  let options = {}

  let reportServiceProp = { sendReport: () => Promise.resolve() }

  beforeEach(() => {
    props = {
      image: { id: 1, url: 'http://foo.bar' },
      providerName: 'provider',
      reportService: reportServiceProp,
    }

    const localVue = createLocalVue()
    localVue.use(VueI18n)

    options = {
      propsData: props,
      i18n,
    }
  })

  it('should contain the correct contents', async () => {
    await render(VContentReportForm, options)
    getCloseButton()
    getDmcaInput()
    getMatureInput()
    getOtherInput()
    getNextButton()
  })

  it('should render thank you note when report is sent', async () => {
    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getNextButton())

    // Thank you message with a link to provider
    getByText('photo-details.content-report.thanks')
    getByText('photo-details.content-report.provider')
  })

  it('should render error message if report sending fails', async () => {
    options.propsData.reportService = { sendReport: () => Promise.reject() }

    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getNextButton())

    // Submission error message
    getByText('photo-details.content-report.submission-error')
    getByText('photo-details.content-report.back')
  })

  it('should render dmca notice', async () => {
    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getDmcaInput())
    await fireEvent.click(getNextButton())

    // Notice with link to provider
    getByText(/dmca/i)
    getByText('photo-details.content-report.provider')
  })

  it('should render other type form', async () => {
    const { getByRole, getByText } = render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())
    await fireEvent.click(getNextButton())

    // Report form with a submit button
    getByText('photo-details.content-report.issue-description')
    getByRole('textbox', {
      name: /description/i,
    })
    getByRole('button', { name: 'photo-details.content-report.submit' })
  })

  it('should dispatch SEND_CONTENT_REPORT on next when mature is selected', async () => {
    const serviceMock = { sendReport: jest.fn() }
    options.propsData.reportService = serviceMock
    render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getNextButton())

    expect(serviceMock.sendReport).toHaveBeenCalledWith({
      identifier: props.image.id,
      reason: 'mature',
      description: '',
    })
  })

  it('should not dispatch SEND_CONTENT_REPORT on next when dmca is selected', async () => {
    const serviceMock = { sendReport: jest.fn() }
    options.propsData.reportService = serviceMock

    render(VContentReportForm, options)
    await fireEvent.click(getDmcaInput())
    await fireEvent.click(getNextButton())

    expect(serviceMock.sendReport).toBeCalledTimes(0)
  })

  it('should dispatch SEND_CONTENT_REPORT on other form submit', async () => {
    const serviceMock = { sendReport: jest.fn() }
    options.propsData.reportService = serviceMock

    const { getByRole } = render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())
    await fireEvent.click(getNextButton())

    const description = 'description that has more than 20 characters'
    await fireEvent.update(getByRole('textbox'), description)
    await fireEvent.click(getByRole('button', { name: /submit/i }))
    expect(serviceMock.sendReport).toHaveBeenCalledWith({
      identifier: props.image.id,
      reason: 'other',
      description,
    })
  })

  it('should not send other report if description is short', async () => {
    options.propsData.reportService = { sendReport: jest.fn() }

    const { getByRole } = render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())
    await fireEvent.click(getNextButton())

    const description = 'short'
    await fireEvent.update(getByRole('textbox'), description)

    expect(getByRole('button', { name: /submit/i })).toBeDisabled()

    // Even though the button is disabled, if we `fireEvent.click`, the report
    // in this test is sent
    // expect(serviceMock.sendReport).toHaveBeenCalledWith({
    //   identifier: props.image.id,
    //   reason: 'other',
    //   description,
    // })
  })
})
