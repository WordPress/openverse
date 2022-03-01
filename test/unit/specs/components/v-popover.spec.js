import Vue from 'vue'
import { render, screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'

import { noFocusableElementWarning } from '~/composables/use-focus-on-show'

import { warn } from '~/utils/console'

import VButton from '~/components/VButton.vue'
import VPopover from '~/components/VPopover/VPopover.vue'

jest.mock('~/utils/console', () => ({
  warn: jest.fn(),
}))

const TestWrapper = Vue.component('TestWrapper', {
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
          <VButton :pressed="visible" v-bind="a11yProps">{{ visible ? 'Close' : 'Open' }}</VButton>
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
const getTrigger = () => screen.getByRole('button')
const getExternalArea = () => screen.getByText(/external area/i)
const clickOutside = () => userEvent.click(getExternalArea())

const doOpen = async (trigger = getTrigger(), verify = true) => {
  await userEvent.click(trigger)
  await nextTick()
  if (verify) {
    expectOpen()
  }
}

const expectOpen = () => {
  expect(getPopover()).toBeVisible()
}

const expectClosed = () => {
  expect(queryPopover().parentElement.parentElement.style.display).toEqual(
    'none'
  )
}

describe('VPopover', () => {
  afterEach(() => {
    warn.mockReset()
  })

  it('should open the popover when the trigger is clicked', async () => {
    render(TestWrapper)

    expectClosed()

    // doOpen already has the visible assertion built in
    await doOpen()
  })

  describe('accessibility', () => {
    it('should render a11y props for the trigger', async () => {
      render(TestWrapper)

      const trigger = getTrigger()

      // This attribute will always exist
      expect(trigger).toHaveAttribute('aria-haspopup', 'dialog')

      // This attribute will only exist when the trigger's related popover is open and the trigger was the current disclosure
      expect(trigger).not.toHaveAttribute('aria-expanded')

      await doOpen(trigger)

      expect(trigger).toHaveAttribute('aria-expanded', 'true')
    })

    describe('autoFocusOnShow', () => {
      it('should focus the popover by default when opening if there is no tabbable content in the popover and warn', async () => {
        render(TestWrapper)
        await doOpen()
        expect(getPopover().parentElement).toHaveFocus()

        expect(warn).toHaveBeenCalledWith(noFocusableElementWarning)
      })

      it('should focus the first tabbable element in the popover by default and not warn', async () => {
        render(TestWrapper, { props: { popoverContentTabIndex: 0 } })
        await doOpen()
        expect(getPopover()).toHaveFocus()
        expect(warn).not.toHaveBeenCalled()
      })

      it('should neither focus no warn when the prop is false', async () => {
        render(TestWrapper, {
          props: { popoverProps: { autoFocusOnShow: false } },
        })
        getTrigger().focus()
        await doOpen()
        expect(getTrigger()).toHaveFocus()
        expect(warn).not.toHaveBeenCalled()
      })
    })

    describe('autoFocusOnHide', () => {
      it('should return focus to the trigger', async () => {
        render(TestWrapper)
        await doOpen()
        await clickOutside()
        expectClosed()
        expect(getTrigger()).toHaveFocus()
      })

      it('should not return focus to the trigger when false', async () => {
        render(TestWrapper, {
          props: { popoverProps: { autoFocusOnHide: false } },
        })
        await doOpen()
        await clickOutside()
        expect(getTrigger()).not.toHaveFocus()
      })
    })
  })

  describe('hideOnClickOutside', () => {
    it('should hide the popover if a click happens outside the popover by default', async () => {
      render(TestWrapper)

      await doOpen()

      await clickOutside()
      expectClosed()
    })

    it('should not hide the popover if a click happens outside the popover when false', async () => {
      render(TestWrapper, {
        props: { popoverProps: { hideOnClickOutside: false } },
      })

      await doOpen()

      await clickOutside()
      expectOpen()
    })
  })

  describe('hideOnEsc', () => {
    it('should hide the popover if escape is sent in the popover by default', async () => {
      render(TestWrapper)
      await doOpen()
      await userEvent.keyboard('{escape}')
      expectClosed()
    })

    it('should not hide if the escape is sent in the popover when false', async () => {
      render(TestWrapper, { props: { popoverProps: { hideOnEsc: false } } })
      await doOpen()
      await userEvent.keyboard('{escape}')
      expectOpen()
    })
  })
})
