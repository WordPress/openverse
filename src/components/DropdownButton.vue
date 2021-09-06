<template>
  <div class="flex flex-col items-end max-w-min">
    <div class="flex" aria-haspopup="menu" :aria-expanded="isOpen">
      <!-- rounded-X-none is required to fight Edge UA styles that apply a 2px border radius to all `button` elements -->
      <button type="button" class="dropdown-button rounded-l-sm rounded-r-none">
        <slot name="button-text" />
      </button>
      <button
        ref="dropdownButton"
        type="button"
        class="dropdown-button ml-1 rounded-r-sm rounded-l-none"
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
    onClickout(e) {
      if (!this.$el.contains(e.target)) {
        this.isOpen = false
      }
    },
    toggleOpen() {
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.focusElement(
          this.$el.querySelector(
            '[role="menu"] [role="menuitem"]:first-of-type'
          )
        )
      } else {
        this.focusElement(this.$refs.dropdownButton.focus())
      }
    },
    focusElement(element) {
      window.setTimeout(() => element.focus(), 0)
    },
  },
}

export default DropdownButton
</script>

<style lang="css" scoped>
.dropdown-button {
  @apply flex items-center justify-center bg-pink text-white font-bold p-2 px-4 transition-shadow duration-100 ease-linear disabled:opacity-70 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-pink;
}

.dropdown-container {
  @apply border border-light-gray rounded-sm px-2 pt-2 pb-1 m-2 max-w-min whitespace-nowrap shadow;
}

.dropdown-item {
  @apply hover:bg-light-gray focus:bg-light-gray px-2 py-1 mb-1 rounded-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-pink;
}
</style>
