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
const getCancelButton = () =>
  screen.getByRole('button', {
    name: /cancel/i,
  })
const getReportButton = () =>
  screen.getByRole('button', {
    name: /submit/i,
  })

// When DMCA selected
const getReportLink = () =>
  screen.getByRole('link', {
    name: /dmca\.open/i,
  })
// When other selected
const getDescriptionTextarea = () =>
  screen.getByRole('textbox', {
    name: /other\.note/i,
  })

describe('VContentReportForm', () => {
  let props = null
  let options = {}

  let reportServiceProp = { sendReport: () => Promise.resolve() }

  beforeEach(() => {
    props = {
      media: {
        identifier: '0aff3595-8168-440b-83ff-7a80b65dea42',
        foreign_landing_url: 'https://wordpress.org/openverse/',
        provider: 'provider',
      },
      providerName: 'Provider',
      closeFn: jest.fn(),
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
    getDmcaInput()
    getMatureInput()
    getOtherInput()
    getCancelButton()
    getReportLink()
  })

  it('should render thank you note when report is sent', async () => {
    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getReportButton())

    // Submission successful message
    getByText('media-details.content-report.success.note')
  })

  it('should render error message if report sending fails', async () => {
    options.propsData.reportService = { sendReport: () => Promise.reject() }

    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getReportButton())

    // Submission error message
    getByText('media-details.content-report.failure.note')
  })

  it('should render DMCA notice', async () => {
    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getDmcaInput())

    // Notice with link to provider
    getByText('media-details.content-report.form.dmca.note')
    getReportLink()
  })

  it('should render other description form', async () => {
    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())

    // Report form with a submit button
    getByText('media-details.content-report.form.other.note')
    getDescriptionTextarea()
  })

  it('should dispatch SEND_CONTENT_REPORT on next when mature is selected', async () => {
    const serviceMock = { sendReport: jest.fn() }
    options.propsData.reportService = serviceMock
    render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getReportButton())

    expect(serviceMock.sendReport).toHaveBeenCalledWith({
      identifier: props.media.identifier,
      reason: 'mature',
      description: '',
    })
  })

  it('should dispatch SEND_CONTENT_REPORT on other form submit', async () => {
    const serviceMock = { sendReport: jest.fn() }
    options.propsData.reportService = serviceMock

    render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())

    const description = 'description that has more than 20 characters'
    await fireEvent.update(getDescriptionTextarea(), description)

    await fireEvent.click(getReportButton())
    expect(serviceMock.sendReport).toHaveBeenCalledWith({
      identifier: props.media.identifier,
      reason: 'other',
      description,
    })
  })

  it('should not send other report if description is short', async () => {
    options.propsData.reportService = { sendReport: jest.fn() }

    render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())

    const description = 'less than 20 chars'
    await fireEvent.update(getDescriptionTextarea(), description)
  })
})
