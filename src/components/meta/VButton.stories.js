import VButton from '~/components/VButton'

export default {
  title: 'Components/VButton',
  component: VButton,
  argTypes: {
    variant: {
      options: [
        'primary',
        'secondary',
        'tertiary',
        'action-menu',
        'action-menu-muted',
      ],
      control: { type: 'radio' },
    },
    as: {
      options: ['button', 'a'],
      control: { type: 'radio' },
    },
    pressed: 'boolean',
    size: {
      options: ['large', 'medium', 'small'],
      control: { type: 'radio' },
    },
    disabled: 'boolean',
    focusableWhenDisabled: 'boolean',
  },
}

const VButtonStory = (args, { argTypes }) => ({
  template: `<VButton v-bind="$props" @click="onClick">Code is Poetry</VButton>`,
  components: { VButton },
  props: Object.keys(argTypes),
  methods: {
    onClick() {
      window.alert('hello!')
    },
  },
})

export const Default = VButtonStory.bind({})
Default.args = {}
