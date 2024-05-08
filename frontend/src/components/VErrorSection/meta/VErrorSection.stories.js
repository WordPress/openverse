import { ECONNABORTED, ERR_UNKNOWN, NO_RESULT } from "~/constants/errors"

import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"

const ErrorPageTemplate = (args) => ({
  template: `<VErrorSection v-bind="args" />`,
  components: { VErrorSection },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VErrorSection",
  component: VErrorSection,
}

export const NoResult = {
  render: ErrorPageTemplate.bind({}),
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

export const ServerTimeout = {
  render: ErrorPageTemplate.bind({}),
  name: "Server timeout",

  args: {
    fetchingError: {
      code: ECONNABORTED,
      requestKind: "search",
      searchType: "image",
    },
  },
}

export const UnknownError = {
  render: ErrorPageTemplate.bind({}),
  name: "Unknown error",

  args: {
    fetchingError: {
      code: ERR_UNKNOWN,
      requestKind: "search",
      searchType: "image",
    },
  },
}
