import { h, ref } from "vue"

import { itemGroupDirections } from "~/types/item-group"

import VItemGroup from "~/components/VItemGroup/VItemGroup.vue"
import VItem from "~/components/VItemGroup/VItem.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VPopover from "~/components/VPopover/VPopover.vue"
import VButton from "~/components/VButton.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VItemGroup",
  component: VItemGroup,
  subcomponents: { VItem, VIcon, VPopover, VButton },

  argTypes: {
    direction: {
      options: itemGroupDirections,
      control: { type: "radio" },
    },

    bordered: {
      control: { type: "boolean" },
    },
  },
} satisfies Meta<typeof VItemGroup>

export default meta
type Story = StoryObj<typeof meta>

const menuDescription =
  'This is a "menu" style item group. Multiple items can be active at a time and all have the "menuitemcheckbox" role.'

type Item = { id: number; label: string; icon: string }
type TriggerProps = {
  a11yProps: Record<string, boolean | string>
  visible: boolean
}

const defaultItem = (
  item: Item,
  idx: number,
  selectedItem: { value: Item }
) => {
  return h(
    VItem,
    {
      key: item.id,
      selected: selectedItem.value.id === item.id,
      isFirst: idx === 0,
      onClick: () => {
        selectedItem.value = item
      },
      size: "medium",
    },
    {
      default: () => [h(VIcon, { name: item.icon }), h("span", {}, item.label)],
    }
  )
}

const menuItem = (
  item: Item,
  idx: number,
  selectedItemIds: { value: Set<number> },
  toggleItem: (item: Item) => void,
  direction?: "vertical" | "horizontal" | "columns"
) =>
  h(
    VItem,
    {
      key: item.id,
      selected: selectedItemIds.value.has(item.id),
      isFirst: idx === 0,
      onClick: () => toggleItem(item),
      size: "medium",
    },
    {
      default: () => [
        h(VIcon, { name: item.icon }),
        h(
          "span",
          { class: direction === "horizontal" ? "pe-2" : "" },
          item.label
        ),
      ],
    }
  )

export const Default: Story = {
  render: (args) => ({
    components: { VItemGroup, VItem, VIcon },
    setup() {
      const icons = ["close", "pause", "play", "replay"]
      const items = new Array(icons.length).fill(null).map((_, i) => ({
        id: i,
        label: `Item ${i}`,
        icon: icons[i],
      }))
      const selectedItem = ref({} as Item)
      return () =>
        h("div", {}, [
          h(
            "p",
            {},
            'This is a "radio" style list group. Only a single element can be selected at a time.'
          ),
          h("div", { style: "width: 300px" }, [
            h(
              VItemGroup,
              { ...args, type: "radiogroup" },
              {
                default: () =>
                  items.map((item, idx) =>
                    defaultItem(item, idx, selectedItem)
                  ),
              }
            ),
          ]),
        ])
    },
  }),
  name: "Default",

  args: {
    direction: "vertical",
    bordered: true,
  },
}

export const Menu: Story = {
  render: (args) => ({
    components: { VItemGroup, VItem, VIcon },
    setup() {
      const icons = ["close", "pause", "play", "replay"]
      const items = new Array(icons.length).fill(null).map((_, i) => ({
        id: i,
        label: `Item ${i}`,
        icon: icons[i],
      }))
      const selectedItemIds = ref(new Set<number>())
      const toggleItem = (item: Item) => {
        if (selectedItemIds.value.delete(item.id)) {
          selectedItemIds.value = new Set(selectedItemIds.value)
        } else {
          selectedItemIds.value = new Set(selectedItemIds.value.add(item.id))
        }
      }
      return () =>
        h("div", {}, [
          h("p", {}, menuDescription),
          h("div", { style: "width: 300px" }, [
            h(
              VItemGroup,
              { ...args, type: "menu" },
              {
                default: () =>
                  items.map((item, idx) =>
                    menuItem(item, idx, selectedItemIds, toggleItem)
                  ),
              }
            ),
          ]),
        ])
    },
  }),
  name: "Menu",

  args: {
    direction: "vertical",
    bordered: true,
  },
}

export const Popover: Story = {
  render: (args) => ({
    components: { VButton, VPopover, VItem, VItemGroup, VIcon },
    setup() {
      const icons = ["close", "pause", "play", "replay"]
      const items = new Array(icons.length).fill(null).map((_, i) => ({
        id: i,
        label: `Item ${i}`,
        icon: icons[i],
      }))
      const selectedItemIds = ref(new Set<number>())
      const toggleItem = (item: Item) => {
        if (selectedItemIds.value.delete(item.id)) {
          selectedItemIds.value = new Set(selectedItemIds.value)
        } else {
          selectedItemIds.value = new Set(selectedItemIds.value.add(item.id))
        }
      }
      return () =>
        h(
          VPopover,
          { id: "item-group-popover" },
          {
            trigger: ({ a11yProps, visible }: TriggerProps) =>
              h(
                VButton,
                {
                  variant: "filled-pink-8",
                  size: "medium",
                  ...a11yProps,
                  pressed: visible,
                },
                { default: () => (visible ? "Close menu" : "Open menu") }
              ),
            default: () => [
              h(
                VItemGroup,
                { ...args, type: "menu" },
                {
                  default: () =>
                    items.map((item, idx) =>
                      menuItem(
                        item,
                        idx,
                        selectedItemIds,
                        toggleItem,
                        args.direction
                      )
                    ),
                }
              ),
            ],
          }
        )
    },
  }),
  name: "Popover",

  args: {
    direction: "vertical",
    bordered: false,
  },
}
