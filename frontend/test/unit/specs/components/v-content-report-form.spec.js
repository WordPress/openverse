/* eslint jest/expect-expect: ["error", { "assertFunctionNames": ["getByText", "getDmcaInput", "getMatureInput", "getOtherInput", "getCancelButton", "getReportButton", "getReportLink", "getDescriptionTextarea", "expect"] }] */

import { fireEvent, screen } from "@testing-library/vue"

import { render } from "~~/test/unit/test-utils/render"

import ReportService from "~/data/report-service"

import VContentReportForm from "~/components/VContentReport/VContentReportForm.vue"

jest.mock("~/composables/use-analytics", () => ({
  useAnalytics: jest.fn(() => ({
    sendCustomEvent: jest.fn(),
  })),
}))

const getDmcaInput = () =>
  screen.getByRole("radio", {
    name: /Infringes copyright/i,
  })
const getMatureInput = () =>
  screen.getByRole("radio", {
    name: /mature/i,
  })
const getOtherInput = () =>
  screen.getByRole("radio", {
    name: /other/i,
  })
const getCancelButton = () =>
  screen.getByRole("button", {
    name: /cancel/i,
  })
const getReportButton = () =>
  screen.getByRole("button", {
    name: /report/i,
  })

// When DMCA selected
const getReportLink = () =>
  screen.getByRole("link", {
    name: /DMCA form/i,
  })
// When other selected
const getDescriptionTextarea = () =>
  screen.getByRole("textbox", {
    name: /Describe the issue. Required/i,
  })

const mockImplementation = () => Promise.resolve()
const mock = jest.fn().mockImplementation(mockImplementation)
jest.mock("~/data/report-service", () => ({
  sendReport: () => mock,
}))

describe("VContentReportForm", () => {
  let props = null
  let options = {}

  beforeEach(() => {
    props = {
      media: {
        id: "0aff3595-8168-440b-83ff-7a80b65dea42",
        foreign_landing_url: "https://wordpress.org/openverse/",
        provider: "provider",
        frontendMediaType: "image",
      },
      providerName: "Provider",
      closeFn: jest.fn(),
    }

    options = {
      propsData: props,
      stubs: ["VIcon"],
    }
  })

  it("should contain the correct contents", async () => {
    await render(VContentReportForm, options)
    getDmcaInput()
    getMatureInput()
    getOtherInput()
    getCancelButton()
    getReportLink()
  })

  it("should render thank you note when report is sent", async () => {
    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getReportButton())

    // Submission successful message
    getByText(/Thank you for reporting this content/i)
  })

  it("should render error message if report sending fails", async () => {
    ReportService.sendReport = () => Promise.reject()

    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getReportButton())

    // Submission error message
    getByText(/Something went wrong, please try again after some time./i)
  })

  it("should render DMCA notice", async () => {
    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getDmcaInput())

    // Notice with link to provider
    getByText(
      /No action will be taken until this form is filled out and submitted/i
    )
    getReportLink()
  })

  it("should render other description form", async () => {
    const { getByText } = render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())

    // Report form with a submit button
    getByText(/Describe the issue./i)
    getDescriptionTextarea()
  })

  it("should dispatch SEND_CONTENT_REPORT on next when mature is selected", async () => {
    ReportService.sendReport = jest.fn()

    render(VContentReportForm, options)
    await fireEvent.click(getMatureInput())
    await fireEvent.click(getReportButton())

    expect(ReportService.sendReport).toHaveBeenCalledWith({
      identifier: props.media.id,
      reason: "mature",
      mediaType: props.media.frontendMediaType,
      description: "",
    })
  })

  it("should send report on other form submit", async () => {
    ReportService.sendReport = jest.fn()

    render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())

    const description = "description that has more than 20 characters"
    await fireEvent.update(getDescriptionTextarea(), description)

    await fireEvent.click(getReportButton())
    expect(ReportService.sendReport).toHaveBeenCalledWith({
      identifier: props.media.id,
      reason: "other",
      mediaType: "image",
      description,
    })
  })

  // @todo this test has no assertions, create an issue to fix it
  // eslint-disable-next-line jest/no-disabled-tests
  it.skip("should not send other report if description is short", async () => {
    ReportService.sendReport = jest.fn()

    render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())

    const description = "less than 20 chars"
    await fireEvent.update(getDescriptionTextarea(), description)
  })
})
