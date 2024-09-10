import { h } from "vue"

import { ECONNABORTED, ERR_UNKNOWN, NO_RESULT } from "~/constants/errors"

import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"

import type { Meta, StoryObj } from "@storybook/vue3"

const meta = {
  title: "Components/VErrorSection",
  component: VErrorSection,
} satisfies Meta<typeof VErrorSection>

export default meta
type Story = StoryObj<typeof meta>

const ErrorPageTemplate: Omit<Story, "args"> = {
  render: (args) => ({
    components: { VErrorSection },
    setup() {
      return () => h(VErrorSection, args)
    },
  }),
}

export const NoResult: Story = {
  ...ErrorPageTemplate,
  name: "No result",

  args: {
    fetchingError: {
      code: NO_RESULT,
      requestKind: "search",
      searchType: "image",

      details: {
        searchTerm: "sad person",
      },
    },
  },
}

export const ServerTimeout: Story = {
  ...ErrorPageTemplate,
  name: "Server timeout",

  args: {
    fetchingError: {
      code: ECONNABORTED,
      requestKind: "search",
      searchType: "image",
    },
  },
}

export const UnknownError: Story = {
  ...ErrorPageTemplate,
  name: "Unknown error",

  args: {
    fetchingError: {
      code: ERR_UNKNOWN,
      requestKind: "search",
      searchType: "image",
    },
  },
}
