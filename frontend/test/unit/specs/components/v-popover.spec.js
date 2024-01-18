import { createApp, nextTick } from "vue"
import { screen } from "@testing-library/vue"
import { default as userEvent } from "@testing-library/user-event"

import { describe, expect, it } from "vitest"

import { render } from "~~/test/unit/test-utils/render"

import VButton from "~/components/VButton.vue"
import VPopover from "~/components/VPopover/VPopover.vue"

const TestWrapper = createApp({}).component("TestWrapper", {
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
          <VButton id="popover-button" variant="bordered-white" size="medium" :pressed="visible" v-bind="a11yProps">{{ visible ? 'Close' : 'Open' }}</VButton>
        </template>
        <div :tabindex="popoverContentTabIndex">Code is Poetry</div>
      </VPopover>
    </div>
  `,
})._context.components.TestWrapper

const getPopover = () => screen.getByRole("dialog", { hidden: true })
const queryPopover = () => screen.queryByRole("dialog", { hidden: true })
const getTrigger = () => screen.getByRole("button", {})
const getExternalArea = () => screen.getByText(/external area/i)
const clickOutside = () => userEvent.click(getExternalArea())

const doOpen = async (trigger = getTrigger()) => {
  await userEvent.click(trigger)
  await nextTick()
}

describe("VPopover", () => {
  it("should open the popover when the trigger is clicked", async () => {
    await render(TestWrapper)

    expect(queryPopover()).not.toBeVisible()

    await doOpen()
    expect(getPopover()).toBeVisible()
  })

  describe("accessibility", () => {
    it("should render a11y props for the trigger", async () => {
      await render(TestWrapper)

      const trigger = getTrigger()

      // This attribute will always exist
      expect(trigger).toHaveAttribute("aria-haspopup", "dialog")

      expect(trigger).toHaveAttribute("aria-expanded", "false")

      await doOpen(trigger)
      expect(getPopover()).toBeVisible()

      expect(trigger).toHaveAttribute("aria-expanded", "true")
    })

    describe("autoFocusOnShow", () => {
      it("should focus the popover by default when opening if there is no tabbable content in the popover and warn", async () => {
        await render(TestWrapper)
        await doOpen()
        expect(getPopover()).toBeVisible()
        expect(getPopover()).toHaveFocus()

        // TODO: Add a spy or a mock for this
        // expect(warn).toHaveBeenCalledWith(noFocusableElementWarning)
      })

      it("should neither focus no warn when the prop is false", async () => {
        await render(TestWrapper, {
          props: { popoverProps: { autoFocusOnShow: false } },
        })
        getTrigger().focus()
        await doOpen()
        expect(getPopover()).toBeVisible()
        expect(getTrigger()).toHaveFocus()
        // TODO: Add a spy or a mock for this
        // expect(warn).not.toHaveBeenCalled()
      })
    })

    describe("autoFocusOnHide", () => {
      it("should return focus to the trigger", async () => {
        await render(TestWrapper, {
          props: { popoverProps: { trapFocus: false } },
        })
        await doOpen()
        expect(getPopover()).toBeVisible()
        await clickOutside()
        expect(queryPopover()).not.toBeVisible()
        expect(getTrigger()).toHaveFocus()
      })

      it("should not return focus to the trigger when false", async () => {
        await render(TestWrapper, {
          props: { popoverProps: { trapFocus: false, autoFocusOnHide: false } },
        })
        await doOpen()
        expect(getPopover()).toBeVisible()
        await clickOutside()
        expect(getTrigger()).not.toHaveFocus()
      })
    })
  })

  describe("hideOnClickOutside", () => {
    it("should hide the popover if a click happens outside the popover by default", async () => {
      await render(TestWrapper)

      await doOpen()
      expect(getPopover()).toBeVisible()
      await clickOutside()
      await nextTick()
      expect(queryPopover()).not.toBeVisible()
    })

    it("should not hide the popover if a click happens outside the popover when false", async () => {
      await render(TestWrapper, {
        props: { popoverProps: { hideOnClickOutside: false } },
      })

      await doOpen()
      expect(getPopover()).toBeVisible()

      await clickOutside()
      expect(getPopover()).toBeVisible()
    })
  })

  describe("hideOnEsc", () => {
    it("should hide the popover if escape is sent in the popover by default", async () => {
      await render(TestWrapper)
      await doOpen()
      expect(getPopover()).toBeVisible()
      await userEvent.keyboard("{escape}")
      expect(queryPopover()).not.toBeVisible()
    })

    it("should not hide if the escape is sent in the popover when false", async () => {
      await render(TestWrapper, {
        props: { popoverProps: { hideOnEsc: false } },
      })
      await doOpen()
      expect(getPopover()).toBeVisible()
      await userEvent.keyboard("{escape}")
      expect(getPopover()).toBeVisible()
    })
  })
})
