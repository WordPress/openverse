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
  expect(screen.findByRole("radio", {
    name: /Infringes copyright/i,
  })).toBeInTheDocument()
const getMatureInput = () =>
  expect(screen.findByRole("radio", {
    name: /mature/i,
  })).toBeInTheDocument()
const getOtherInput = () =>
  expect(screen.findByRole("radio", {
    name: /other/i,
  })).toBeInTheDocument()
const getCancelButton = () =>
  expect(screen.findByRole("button", {
    name: /cancel/i,
  })).toBeInTheDocument()
const getReportButton = () =>
  expect(screen.findByRole("button", {
    name: /report/i,
  })).toBeInTheDocument()

// When DMCA selected
const getReportLink = () =>
  expect(screen.findByRole("link", {
    name: /DMCA form/i,
  })).toBeInTheDocument()
// When other selected
const getDescriptionTextarea = () =>
  expect(screen.findByRole("textbox", {
    name: /Describe the issue. Required/i,
  })).toBeInTheDocument()

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

  it("submit button on other form should only be enabled if input is longer than 20 characters", async () => {
    ReportService.sendReport = jest.fn()

    render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())

    // The minimum length for report description is 20 characters. This is invalid
    const description = "1234567890123456789"
    await fireEvent.update(getDescriptionTextarea(), description)

    // The button is not fully disabled, it uses `aria-disabled` attribute so that
    // it remains focusable for screen readers to access the context.
    expect(await getReportButton()).toHaveAttribute("aria-disabled", "true")

    await fireEvent.update(getDescriptionTextarea(), description + "0") // Valid, 20 characters
    expect(getReportButton()).not.toHaveAttribute("aria-disabled")
  })
})
