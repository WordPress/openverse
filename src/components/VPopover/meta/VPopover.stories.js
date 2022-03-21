import { placements as popoverPlacements } from '@popperjs/core'

import { log } from '~/utils/console'

import VPopover from '~/components/VPopover/VPopover.vue'
import VButton from '~/components/VButton.vue'

export default {
  component: VPopover,
  title: 'Components/VPopover',
  argTypes: {
    hideOnEsc: 'boolean',
    hideOnClickOutside: 'boolean',
    autoFocusOnShow: 'boolean',
    autoFocusOnHide: 'boolean',
    placement: {
      type: 'radio',
      options: [...popoverPlacements],
    },
    label: 'text',
    labelledBy: 'text',
  },
}

const SinglePopoverStory = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  template: `
    <div>
      <p>
        This story is configured to log when the popover opens or closes. Inspect the console output to observe this behavior.
      </p>
      <div tabindex="0">Focusable external area</div>
      <VPopover v-bind="$props" @open="onOpen" @close="onClose">
        <template #trigger="{ visible, a11yProps }">
          <VButton :pressed="visible" v-bind="a11yProps">{{ visible ? 'Close' : 'Open' }}</VButton>
        </template>
        <div class="py-1 px-2">Code is Poetry</div>
      </VPopover>
    </div>
  `,
  components: { VPopover, VButton },
  setup() {
    const onOpen = () => log('opened!')
    const onClose = () => log('closed!')

    return { onOpen, onClose }
  },
})

export const Default = SinglePopoverStory.bind({})
Default.args = {}

const ControlStory = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  template: `
    <VPopover>
      <template #trigger="{ visible, a11yProps }">
        <VButton :pressed="visible" v-bind="a11yProps">{{ visible ? 'Close' : 'Open' }}</VButton>
      </template>
      <template #default="{ close }">
        <div class="p-4">
        <VButton @click="close">Close popover</VButton>
        </div>
      </template>
    </VPopover>
  `,
})

export const Control = ControlStory.bind({})
Control.args = {}

const TwoPopoverStory = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  template: `
    <div>
      <VPopover label="First popover" v-bind="$props">
        <template #trigger="{ visible, a11yProps }">
          <VButton :pressed="visible" v-bind="a11yProps">{{ visible ? 'First popover open' : 'First popover closed' }}</VButton>
        </template>
        <div class="py-1 px-2">First popover content</div>
      </VPopover>
      <div class="h-5">Some content</div>
      <VPopover label="Second popover" v-bind="$props">
        <template #trigger="{ visible, a11yProps }">
          <VButton :pressed="visible" v-bind="a11yProps">{{ visible ? 'Second popover open' : 'Second popover closed' }}</VButton>
        </template>
        <div class="py-1 px-2">Second popover content</div>
      </VPopover>
    </div>
  `,
  components: { VPopover, VButton },
})

export const TwoPopovers = TwoPopoverStory.bind({})
TwoPopovers.args = {}
