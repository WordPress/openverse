import DropdownButton from '~/components/DropdownButton'

export default {
  title: 'Components/DropdownButton',
  component: DropdownButton,
}

export const Default = () => `
<DropdownButton>
  <template v-slot:button-text>
    Download
  </template>

  <template v-slot:items="{ itemClass, itemA11yProps, toggleOpen }">
    <ul>
      <li><button :class="itemClass" type="button" v-bind="itemA11yProps" @click="toggleOpen">Item 1</button></li>
      <li><button :class="itemClass" type="button" v-bind="itemA11yProps" @click="toggleOpen">Item 2</button></li>
    </ul>
  </template>
</DropdownButton>
`
