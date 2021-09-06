import DropdownButton from '~/components/DropdownButton'

export default {
  title: 'Components/DropdownButton',
  component: DropdownButton,
}

export const Default = () => ({
  template: `
    <div>
      <DropdownButton>
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
  data: () => ({
    items: [
      { name: 'Item 1', active: false },
      { name: 'Item 2', active: false },
    ],
  }),
  computed: {
    activeItem() {
      return this.items.find((item) => item.active)
    },
  },
  methods: {
    onClick(event) {
      console.log(event)
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
