<template>
  <div class="flex flex-col items-end max-w-min">
    <div class="flex" aria-haspopup="menu" :aria-expanded="isOpen">
      <!-- rounded-X-none is required to fight Edge UA styles that apply a 2px border radius to all `button` elements -->
      <slot
        :button-props="{
          class: 'dropdown-button rounded-l-sm rounded-r-none',
          type: 'button',
        }"
      />
      <button
        ref="dropdownButton"
        type="button"
        class="dropdown-button ml-1 rounded-r-sm rounded-l-none"
        :class="{ 'dropdown-button-active': isOpen }"
        @click="toggleOpen"
        @keydown.enter="toggleOpen"
        @keydown.space.prevent="toggleOpen"
      >
        <svg class="h-2 w-4">
          <use :href="`${icons.caretDown}#icon`" />
        </svg>
      </button>
    </div>

    <div
      ref="dropdownContainer"
      class="dropdown-container"
      :class="{ hidden: !isOpen }"
      role="menu"
      :aria-hidden="!isOpen"
    >
      <slot
        name="items"
        :item-class="'dropdown-item'"
        :item-a11y-props="{ role: 'menuitem' }"
        :toggle-open="toggleOpen"
        :active-item-class="'dropdown-item-active'"
        :on-item-keydown="onItemKeydown"
      />
    </div>
  </div>
</template>

<script>
import caretDown from '~/assets/icons/caret-down.svg'

const DropdownButton = {
  name: 'DropdownButton',
  data: () => ({
    isOpen: false,
    icons: {
      caretDown,
    },
  }),
  mounted() {
    document.addEventListener('click', this.onClickout)
  },
  beforeDestroy() {
    document.removeEventListener('click', this.onClickout)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.onClickout)
  },
  methods: {
    getItems() {
      return Array.from(
        this.$refs.dropdownContainer.querySelectorAll('[role="menuitem"]')
      )
    },
    onClickout(e) {
      if (
        e.target !== this.$refs.dropdownButton &&
        !this.$refs.dropdownContainer.contains(e.target)
      ) {
        this.isOpen = false
      }
    },
    toggleOpen() {
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.focusElement(this.getItems()[0])
      } else {
        this.focusElement(this.$refs.dropdownButton)
      }
    },
    focusElement(element) {
      window.setTimeout(() => element.focus(), 0)
    },
    onItemKeydown(event) {
      const items = this.getItems()
      const itemIndex = items.findIndex((item) => item === event.target)
      console.log(event)
      if (event.key === 'ArrowUp') {
        if (itemIndex === 0) {
          // don't do anything if pressing up on the first item
          return
        }
        this.focusElement(items[itemIndex - 1])
      } else if (event.key === 'ArrowDown') {
        if (itemIndex === items.length - 1) {
          // don't do anything if pressing down on the last item
          return
        }
        this.focusElement(items[itemIndex + 1])
      }
    },
  },
}

export default DropdownButton
</script>

<style lang="css" scoped>
.dropdown-button {
  @apply flex items-center justify-center bg-pink text-white font-bold p-2 px-4 transition-shadow duration-100 ease-linear disabled:opacity-70 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-pink;
}

.dropdown-button-active {
  @apply bg-dark-pink;
}

.dropdown-container {
  @apply border border-light-gray rounded-sm px-2 pt-2 pb-1 m-2 max-w-min whitespace-nowrap shadow;
}

.dropdown-item {
  @apply hover:bg-light-gray px-2 py-1 mb-1 rounded-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-pink;
}

.dropdown-item-active {
  @apply bg-light-gray;
}
</style>
