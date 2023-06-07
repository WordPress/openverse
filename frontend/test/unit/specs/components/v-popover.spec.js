/* eslint jest/expect-expect: ["error", { "assertFunctionNames": ["getPopover", "getTrigger", "getExternalArea", "expectOpen", "doOpen", "expectClosed"] } ] */

import Vue from "vue"
import { screen } from "@testing-library/vue"
import userEvent from "@testing-library/user-event"

import { render } from "~~/test/unit/test-utils/render"

import { noFocusableElementWarning } from "~/composables/use-focus-on-show"

import { warn } from "~/utils/console"

import VButton from "~/components/VButton.vue"
import VPopover from "~/components/VPopover/VPopover.vue"

jest.mock("~/utils/console", () => ({
  warn: jest.fn(),
}))

const TestWrapper = Vue.component("TestWrapper", {
  components: { VButton, VPopover },
  props: {
    popoverProps: {
      type: Object,
      default: () => ({}),
    },
    popoverContentTabIndex: {
      type: Number,
      default: undefined,
    },
  },
  template: `
    <div>
      <!-- This div is a clickable area that is neither the trigger nor the content, useful for testing click-away behavior -->
      <div>External area</div>
      <VPopover label="Test label" v-bind="popoverProps">
        <template #trigger="{ visible, a11yProps }">
          <VButton variant="bordered-white" size="medium" :pressed="visible" v-bind="a11yProps">{{ visible ? 'Close' : 'Open' }}</VButton>
        </template>
        <div :tabindex="popoverContentTabIndex">Code is Poetry</div>
      </VPopover>
    </div>
  `,
})

const nextTick = async () =>
  await new Promise((resolve) => setTimeout(resolve, 1))

const getPopover = () => screen.getByText(/code is poetry/i)
const queryPopover = () => screen.queryByText(/code is poetry/i)
const getTrigger = () => screen.getByRole("button", {})
const getExternalArea = () => screen.getByText(/external area/i)
const clickOutside = () => userEvent.click(getExternalArea())

const doOpen = async (trigger = getTrigger()) => {
  await userEvent.click(trigger)
  await nextTick()
}

const expectOpen = () => {
  expect(getPopover()).toBeVisible()
}

describe("VPopover", () => {
  afterEach(() => {
    warn.mockReset()
  })

  it("should open the popover when the trigger is clicked", async () => {
    render(TestWrapper)

    expect(queryPopover()).not.toBeInTheDocument()

    await doOpen()
    expectOpen()
  })

  describe("accessibility", () => {
    it("should render a11y props for the trigger", async () => {
      render(TestWrapper)

      const trigger = getTrigger()

      // This attribute will always exist
      expect(trigger).toHaveAttribute("aria-haspopup", "dialog")

      // This attribute will only exist when the trigger's related popover is open and the trigger was the current disclosure
      expect(trigger).not.toHaveAttribute("aria-expanded")

      await doOpen(trigger)
      expectOpen()

      expect(trigger).toHaveAttribute("aria-expanded", "true")
    })

    describe("autoFocusOnShow", () => {
      it("should focus the popover by default when opening if there is no tabbable content in the popover and warn", async () => {
        render(TestWrapper)
        await doOpen()
        expectOpen()
        expect(getPopover().parentElement).toHaveFocus()

        expect(warn).toHaveBeenCalledWith(noFocusableElementWarning)
      })

      // https://github.com/WordPress/openverse/issues/2300
      // eslint-disable-next-line jest/no-disabled-tests
      it.skip("should focus the first tabbable element in the popover by default and not warn", async () => {
        render(TestWrapper, { props: { popoverContentTabIndex: 0 } })
        await doOpen()
        expectOpen()
        await nextTick()
        expect(getPopover()).toHaveFocus()
        expect(warn).not.toHaveBeenCalled()
      })

      it("should neither focus no warn when the prop is false", async () => {
        render(TestWrapper, {
          props: { popoverProps: { autoFocusOnShow: false } },
        })
        getTrigger().focus()
        await doOpen()
        expectOpen()
        expect(getTrigger()).toHaveFocus()
        expect(warn).not.toHaveBeenCalled()
      })
    })

    describe("autoFocusOnHide", () => {
      it("should return focus to the trigger", async () => {
        render(TestWrapper, {
          props: { popoverProps: { trapFocus: false } },
        })
        await doOpen()
        expectOpen()
        await clickOutside()
        expect(queryPopover()).not.toBeVisible()
        expect(getTrigger()).toHaveFocus()
      })

      it("should not return focus to the trigger when false", async () => {
        render(TestWrapper, {
          props: { popoverProps: { trapFocus: false, autoFocusOnHide: false } },
        })
        await doOpen()
        expectOpen()
        await clickOutside()
        expect(getTrigger()).not.toHaveFocus()
      })
    })
  })

  describe("hideOnClickOutside", () => {
    // This test is broken (for some reason clickOutside does not appear to actually cause a click
    // to happen in this case).
    // https://github.com/WordPress/openverse/issues/2220
    // eslint-disable-next-line jest/no-disabled-tests
    it.skip("should hide the popover if a click happens outside the popover by default", async () => {
      render(TestWrapper)

      await doOpen()
      expectOpen()
      await clickOutside()
      await nextTick()
      expect(queryPopover()).not.toBeVisible()
    })

    it("should not hide the popover if a click happens outside the popover when false", async () => {
      render(TestWrapper, {
        props: { popoverProps: { hideOnClickOutside: false } },
      })

      await doOpen()
      expectOpen()

      await clickOutside()
      expectOpen()
    })
  })

  describe("hideOnEsc", () => {
    it("should hide the popover if escape is sent in the popover by default", async () => {
      render(TestWrapper)
      await doOpen()
      expectOpen()
      await userEvent.keyboard("{escape}")
      expect(queryPopover()).not.toBeVisible()
    })

    it("should not hide if the escape is sent in the popover when false", async () => {
      render(TestWrapper, { props: { popoverProps: { hideOnEsc: false } } })
      await doOpen()
      expectOpen()
      await userEvent.keyboard("{escape}")
      expectOpen()
    })
  })
})
