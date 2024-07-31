import VContentSettingsButton from "~/components/VHeader/VHeaderMobile/VContentSettingsButton.vue"
import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"

const Template = (args) => ({
  template: `<div class="wrapper border-dark-charcoal-10 inline-flex justify-start p-2">
    <VSearchBarButton label="VSearchBarButton" :icon="args.icon" v-bind="args" v-on="args" />
  </div>`,
  components: { VSearchBarButton },
  setup() {
    if (!args.icon) {
      args.icon = "close"
    }
    return { args }
  },
})

const contentSettingsTemplate = (args) => ({
  template: `
    <div class="wrapper rounded-sm inline-flex justify-end bg-dark-charcoal-10">
    <VContentSettingsButton label="VContentSettingsButton" :are-filters-selected="true" v-bind="args" />
    </div>
  `,
  components: { VContentSettingsButton },
  setup() {
    return { args }
  },
})

const activeButtonsTemplate = (args) => ({
  template: `<div class="wrapper rounded-sm bg-white flex justify-between ring ring-pink-8-8">
  <VSearchBarButton
    icon="chevron-back"
    :label="$t('header.back-button')"
    variant="filled-gray"
    :rtl-flip="true"
  />
  <VSearchBarButton
    icon="close-small"
    :label="$t('browsePage.searchForm.clear')"
    variant="transparent-gray"
  />
</div>`,
  components: { VContentSettingsButton, VSearchBarButton },
  setup() {
    return { args }
  },
})

export default {
  title: "Components/VHeader/VHeaderMobile/VSearchBarButton",
  component: VSearchBarButton,

  argTypes: {
    icon: {
      control: {
        type: "select",
        default: "close-small",
      },

      options: ["close-small", "chevron-back", "source"],
    },

    rtlFlip: {
      control: {
        type: "boolean",
      },
    },

    variant: {
      control: {
        type: "select",
      },

      options: [
        "filled-white",
        "filled-gray",
        "transparent-gray",
        "transparent-dark",
      ],
    },

    click: {
      action: "click",
    },
  },
}

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    icon: "close-small",
    label: "VSearchBarButton",
    variant: "filled-white",
  },
}

export const ContentSettingsButtonWithFiltersSelected = {
  render: contentSettingsTemplate.bind({}),
  name: "Content Settings Button with filters selected",
}

export const ClearAndBackButtons = {
  render: activeButtonsTemplate.bind({}),
  name: "Clear and Back Buttons",
}
