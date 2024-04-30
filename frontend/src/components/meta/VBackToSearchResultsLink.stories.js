import VBackToSearchResultsLink from "~/components/VBackToSearchResultsLink.vue"

const Template = () => ({
  template: `<VBackToSearchResultsLink href="#" id="123" />`,
  components: { VBackToSearchResultsLink },
})

export default {
  title: "Components/VBackToSearchResultsLink",
  component: VBackToSearchResultsLink,
}

export const Default = {
  render: Template.bind({}),
  name: "Default",
}
