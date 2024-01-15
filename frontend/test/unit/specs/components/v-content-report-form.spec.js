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
  screen.queryByRole("radio", {
    name: /Infringes copyright/i,
  })
const getSensitiveInput = () =>
  screen.queryByRole("radio", {
    name: /sensitive/i,
  })
const getOtherInput = () =>
  screen.queryByRole("radio", {
    name: /other/i,
  })
const getCancelButton = () =>
  screen.queryByRole("button", {
    name: /cancel/i,
  })
const getReportButton = () =>
  screen.queryByRole("button", {
    name: /report/i,
  })

// When DMCA selected
const getReportLink = () =>
  screen.queryByRole("link", {
    name: /DMCA form/i,
  })
// When other selected
const getDescriptionTextarea = () =>
  screen.queryByRole("textbox", {
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
    expect(getDmcaInput()).toBeVisible()
    expect(getSensitiveInput()).toBeVisible()
    expect(getOtherInput()).toBeVisible()
    expect(getCancelButton()).toBeVisible()
    // By default, DMCA is selected, and we show a link to
    // the report form instead of a report button.
    expect(getReportButton()).not.toBeInTheDocument()
    expect(getReportLink()).toBeVisible()
  })

  it("should render thank you note when report is sent", async () => {
    const { queryByText } = render(VContentReportForm, options)
    await fireEvent.click(getSensitiveInput())
    await fireEvent.click(getReportButton())

    // Submission successful message
    expect(
      queryByText(/Thank you for reporting this content/i)
    ).toBeInTheDocument()
  })

  it("should render error message if report sending fails", async () => {
    ReportService.sendReport = () => Promise.reject()

    const { queryByText } = render(VContentReportForm, options)
    await fireEvent.click(getSensitiveInput())
    await fireEvent.click(getReportButton())

    // Submission error message
    expect(
      queryByText(/Something went wrong, please try again after some time./i)
    ).toBeInTheDocument()
  })

  it("should render DMCA notice", async () => {
    const { queryByText } = render(VContentReportForm, options)
    await fireEvent.click(getDmcaInput())

    // Notice with link to provider
    expect(
      queryByText(
        /No action will be taken until this form is filled out and submitted/i
      )
    ).toBeInTheDocument()
    getReportLink()
  })

  it("should render other description form", async () => {
    const { queryByText } = render(VContentReportForm, options)
    await fireEvent.click(getOtherInput())

    // Report form with a submit button
    expect(queryByText(/Describe the issue./i)).toBeInTheDocument()
    getDescriptionTextarea()
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
