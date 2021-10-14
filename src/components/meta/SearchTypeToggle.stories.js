import SearchTypeToggle from '~/components/SearchTypeToggle'

export default {
  title: 'Components/SearchTypeToggle',
  component: SearchTypeToggle,
}

export const Default = () => ({
  template: `
    <div>
      <p>Selected search type: {{ searchType }}</p>
      <SearchTypeToggle v-model="searchType" />
    </div>
  `,
  data() {
    return { searchType: 'audio' }
  },
})
