import { h, ref } from "vue"

import VSearchBar from "~/components/VHeader/VSearchBar/VSearchBar.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VHeader/Search bar",
  component: VSearchBar,

  argTypes: {
    onSubmit: { action: "submit" },
  },
} satisfies Meta<typeof VSearchBar>

export default meta
type Story = StoryObj<typeof meta>
type StoryTemplate = Omit<Story, "args">

const Template: StoryTemplate = {
  render: (args) => ({
    components: { VSearchBar },
    setup() {
      return () =>
        h(
          VSearchBar,
          { ...args },
          {
            default: () =>
              h(
                "span",
                {
                  class:
                    "info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",
                },
                "12,345 results"
              ),
          }
        )
    },
  }),
}

export const Default = {
  ...Template,
  name: "Default",

  args: {
    value: "Search query",
  },
}

export const VModel: Story = {
  render: (args) => ({
    components: { VSearchBar },
    setup() {
      const text = ref("Hello, World!")
      const updateText = (event: Event) => {
        const target = event.target as HTMLInputElement
        text.value = target.value
      }
      return () =>
        h("div", [
          h(
            VSearchBar,
            { ...args },
            {
              default: () =>
                h(
                  "span",
                  {
                    class:
                      "info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",
                    onChange: updateText,
                  },
                  `${text.value.length} chars`
                ),
            }
          ),
          text.value,
        ])
    },
  }),
  name: "v-model",
}

export const WithPlaceholder = {
  ...Template,
  name: "With placeholder",

  args: {
    placeholder: "Search query",
  },
}
