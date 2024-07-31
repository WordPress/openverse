import VPopover from "~/components/VPopover/VPopover.vue"
import VButton from "~/components/VButton.vue"

const popoverPlacements = [
  "top",
  "top-start",
  "top-end",
  "bottom",
  "bottom-start",
  "bottom-end",
  "left",
  "left-start",
  "left-end",
  "right",
  "right-start",
  "right-end",
]

const DefaultPopoverStory = (args) => ({
  template: `
    <div>
      <p>
        This story is configured to log when the popover opens or closes. Inspect the Actions tab to observe this behavior.
      </p>
      <div tabindex="0">Focusable external area</div>
      <VPopover v-bind="args" v-on="args" v-for="item in args.popoverItems" :key="item" class="mb-2">
        <template #trigger="{ visible, a11yProps }">
          <VButton :pressed="visible" variant="filled-pink-8-8" size="medium" v-bind="a11yProps">{{
              visible ? 'Close' : 'Open'
           }}</VButton>
        </template>
        <div class="py-1 px-2">Code is Poetry</div>
      </VPopover>
    </div>
  `,
  components: { VPopover, VButton },
  setup() {
    return { args }
  },
})

const ControlStory = (args) => ({
  template: `
    <VPopover v-bind="args" v-on="args">
      <template #trigger="{ visible, a11yProps }">
        <VButton :pressed="visible" variant="filled-pink-8-8" size="medium" v-bind="a11yProps">{{
            visible ? 'Close' : 'Open'
        }}</VButton>
      </template>
      <template #default="{ close }">
        <div class="p-4">
        <VButton variant="filled-gray" size="medium"  @click="close">Close popover</VButton>
        </div>
      </template>
    </VPopover>
  `,
  components: { VPopover, VButton },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VPopover",
  components: VPopover,

  argTypes: {
    hideOnEsc: {
      control: {
        type: "boolean",
      },
    },

    hideOnClickOutside: {
      control: {
        type: "boolean",
      },
    },

    autoFocusOnShow: {
      control: {
        type: "boolean",
      },
    },

    autoFocusOnHide: {
      control: {
        type: "boolean",
      },
    },

    placement: {
      options: [...popoverPlacements],

      control: {
        type: "radio",
      },
    },

    label: {
      control: {
        type: "text",
      },
    },

    labelledBy: {
      control: {
        type: "text",
      },
    },

    close: {
      action: "close",
    },

    open: {
      action: "open",
    },

    popoverItems: {
      control: {
        type: "number",
      },
    },
  },
}

export const Default = {
  render: DefaultPopoverStory.bind({}),
  name: "Default",

  args: {
    popoverItems: 1,
  },
}

export const Control = {
  render: ControlStory.bind({}),
  name: "Control",
}

export const TwoPopovers = {
  render: DefaultPopoverStory.bind({}),
  name: "Two Popovers",

  args: {
    popoverItems: 2,
  },
}
