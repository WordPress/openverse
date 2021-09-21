<template>
  <div class="relative block max-w-min">
    <!-- rounded-X-none is required to fight Edge UA styles that apply a 2px border radius to all `button` elements -->
    <div class="flex">
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
        aria-haspopup="menu"
        :aria-label="safeDropdownAriaLabel"
        :aria-expanded="isOpen"
        @click="toggleOpen"
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
      @focusout="onFocusout"
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
  props: {
    dropdownAriaLabel: {
      type: String,
      required: false,
    },
  },
  data() {
    return {
      isOpen: false,
      icons: {
        caretDown,
      },
      safeDropdownAriaLabel:
        this.dropdownAriaLabel || this.$t('dropdown-button.aria.arrow-label'),
    }
  },
  mounted() {
    document.addEventListener('click', this.onClickout)
  },
  beforeDestroy() {
    document.removeEventListener('click', this.onClickout)
  },
  methods: {
    getItems() {
      return Array.from(
        this.$refs.dropdownContainer.querySelectorAll('[role="menuitem"]')
      )
    },
    onClickout(event) {
      if (
        event.target !== this.$refs.dropdownButton &&
        !this.$refs.dropdownContainer.contains(event.target)
      ) {
        this.isOpen = false
      }
    },
    onFocusout(event) {
      if (!this.$el.contains(event.relatedTarget)) {
        this.toggleOpen()
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
      switch (event.key) {
        case 'ArrowUp': {
          if (itemIndex === 0) {
            // don't do anything if pressing up on the first item
            return
          }
          this.focusElement(items[itemIndex - 1])
          break
        }
        case 'ArrowDown': {
          if (itemIndex === items.length - 1) {
            // don't do anything if pressing down on the last item
            return
          }
          this.focusElement(items[itemIndex + 1])
          break
        }
        case 'Escape': {
          this.toggleOpen()
          break
        }
        case 'Home':
        case 'PageUp': {
          this.focusElement(items[0])
          break
        }
        case 'End':
        case 'PageDown': {
          this.focusElement(items[items.length - 1])
          break
        }
      }
    },
  },
}

export default DropdownButton
</script>

<style lang="css" scoped>
.dropdown-button {
  @apply flex items-center justify-center bg-pink text-white font-bold p-2 px-4 transition-shadow duration-100 ease-linear disabled:opacity-70 focus:outline-none focus-visible:ring focus-visible:ring-offset-2 focus-visible:ring-pink hover:bg-dark-pink;
}

.dropdown-button-active {
  @apply bg-dark-pink;
}

.dropdown-container {
  @apply absolute right-0 z-50 bg-white border border-light-gray rounded-sm px-2 pt-2 pb-1 mt-2 max-w-min whitespace-nowrap shadow;
}

.dropdown-item {
  @apply hover:bg-light-gray px-2 py-1 mb-1 rounded-sm transition-colors focus:outline-none focus:ring focus:ring-offset-2 focus:ring-pink;
}

.dropdown-item-active {
  @apply bg-light-gray;
}
</style>
