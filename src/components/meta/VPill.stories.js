import VPill from '~/components/VPill.vue'

export default {
  title: 'Components/VPill',
  component: VPill,
}

const DefaultStory = () => ({
  template: `<VPill>Beta</VPill>`,
})
export const Default = DefaultStory.bind({})
Default.args = {}
