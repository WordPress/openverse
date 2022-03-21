import { log } from '~/utils/console'

import DropdownButton from '~/components/DropdownButton.vue'

export default {
  title: 'Components/DropdownButton',
  component: DropdownButton,
  argTypes: {
    size: {
      type: 'select',
      options: ['medium', 'small'],
    },
  },
}

export const Default = (args, { argTypes }) => ({
  template: `
    <div>
      <DropdownButton v-bind="$props">
        <template #default="{ buttonProps }">
          <button v-bind="buttonProps" class="whitespace-nowrap" @click="onClick">Download {{ activeItem?.name ?? '' }}</button>
        </template>

        <template #items="{ activeItemClass, itemClass, itemA11yProps, toggleOpen, onItemKeydown }">
          <ul>
            <li v-for="item in items" :key="item.name">
              <button :class="{ [itemClass]: true, [activeItemClass]: item.active }" type="button" v-bind="itemA11yProps" @click="setActive(item); toggleOpen()" @keydown="onItemKeydown">{{ item.name }}</button>
            </li>
          </ul>
        </template>
      </DropdownButton>
      Test element below
    </div>
  `,
  props: Object.keys(argTypes).filter((i) => i !== 'items'),
  data() {
    return {
      items: [
        { name: 'Item 1', active: false },
        { name: 'Item 2', active: false },
      ],
    }
  },
  computed: {
    activeItem() {
      log(this)
      return this.items.find((item) => item.active)
    },
  },
  methods: {
    onClick(event) {
      log(event)
      alert('clicked!')
    },
    setActive(toActivate) {
      this.items = this.items.map((item) => ({
        ...item,
        active: item === toActivate,
      }))
    },
  },
})
