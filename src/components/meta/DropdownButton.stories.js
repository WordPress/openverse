import DropdownButton from '~/components/DropdownButton'

export default {
  title: 'Components/DropdownButton',
  component: DropdownButton,
}

export const Default = () => ({
  template: `
    <DropdownButton>
      <template #default="{ buttonProps }">
        <button v-bind="buttonProps" @click="onClick">Download</button>
      </template>

      <template #items="{ itemClass, itemA11yProps, toggleOpen }">
        <ul>
          <li><button :class="itemClass" type="button" v-bind="itemA11yProps" @click="toggleOpen">Item 1</button></li>
          <li><button :class="itemClass" type="button" v-bind="itemA11yProps" @click="toggleOpen">Item 2</button></li>
        </ul>
      </template>
    </DropdownButton>
  `,
  methods: {
    onClick(event) {
      console.log(event)
      alert('clicked!')
    },
  },
})
