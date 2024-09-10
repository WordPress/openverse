import { h } from "vue"

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

export default {
  title: "Components/VPopover",
  components: VPopover,

  argTypes: {
    hideOnEsc: { control: { type: "boolean" } },

    hideOnClickOutside: { control: { type: "boolean" } },

    autoFocusOnShow: { control: { type: "boolean" } },

    autoFocusOnHide: { control: { type: "boolean" } },

    placement: { options: [...popoverPlacements], control: { type: "radio" } },

    label: { control: { type: "text" } },

    labelledBy: { control: { type: "text" } },

    onClose: { action: "close" },

    onOpen: { action: "open" },

    popoverItems: { control: { type: "number" } },
  },
  args: {
    id: "popover-story",
    hideOnEsc: true,
    hideOnClickOutside: true,
    autoFocusOnShow: true,
    autoFocusOnHide: true,
    placement: "bottom",
    label: "Code is Poetry",
    labelledBy: "popover-story",
  },
}

const DefaultPopoverStory = (args) => ({
  components: { VPopover, VButton },
  setup() {
    return () =>
      h("div", [
        h(
          "p",
          "This story is configured to log when the popover opens or closes. Inspect the Actions tab to observe this behavior."
        ),
        h("div", { tabindex: "0" }, "Focusable external area"),
        ...Array(args.popoverItems)
          .fill()
          .map((_, item) =>
            h(
              VPopover,
              {
                ...args,
                key: item,
                class: "mb-2",
                onClose: args.onClose,
                onOpen: args.onOpen,
              },
              {
                trigger: ({ visible, a11yProps }) =>
                  h(
                    VButton,
                    {
                      pressed: visible,
                      variant: "filled-pink-8",
                      size: "medium",
                      ...a11yProps,
                    },
                    () => (visible ? "Close" : "Open")
                  ),
                default: () =>
                  h("div", { class: "py-1 px-2" }, "Code is Poetry"),
              }
            )
          ),
      ])
  },
})

const ControlStory = (args) => ({
  components: { VPopover, VButton },
  setup() {
    return () =>
      h(
        VPopover,
        {
          ...args,
          onClose: args.onClose,
          onOpen: args.onOpen,
        },
        {
          trigger: ({ visible, a11yProps }) =>
            h(
              VButton,
              {
                pressed: visible,
                variant: "filled-pink-8",
                size: "medium",
                ...a11yProps,
              },
              () => (visible ? "Close" : "Open")
            ),
          default: ({ close }) =>
            h("div", { class: "p-4" }, [
              h(
                VButton,
                {
                  variant: "filled-gray",
                  size: "medium",
                  onClick: close,
                },
                () => "Close popover"
              ),
            ]),
        }
      )
  },
})

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
