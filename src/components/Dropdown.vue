<template>
  <!-- Copied and modified from Vuetensils to match the existing bulma implementation -->
  <!-- https://github.com/AustinGil/vuetensils/blob/production/src/components/VDropdown/VDropdown.vue -->
  <div
    class="navbar-item has-dropdown is-hoverable"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @focus="isFocused = true"
    @blur="isFocused = false"
    @focusout="onFocusout"
  >
    <div
      :aria-expanded="isHovered || isFocused"
      aria-haspopup="true"
      class="navbar-link is-arrowless"
      role="button"
      tabindex="0"
      @keydown.enter="isFocused = !isFocused"
      @keydown.space.prevent="isFocused = !isFocused"
      @click="isFocused = !isFocused"
      @focus="isFocused = true"
    >
      {{ text }}
      <i class="icon caret-down" />
    </div>

    <div
      class="navbar-dropdown"
      :class="{ visible: isHovered || isFocused }"
      role="menu"
    >
      <slot :onFocus="onFocus" />
    </div>
  </div>
</template>

<script>
/**
 * Mimics the behavior of the WordPress.org menubar. Creates an accessible focusable trigger element that
 * when focused, opens an accessible dropdown menu.
 *
 * This does not fully follow the ARIA specification/recommendation for accessible dropdown in order to stay
 * consistent with the WordPress.org menubar. For example, it does not implement arrow key navigation,
 * instead just allowing for tab navigation through each item.
 */
const Dropdown = {
  name: 'Dropdown',
  props: {
    /**
     * The trigger element text.
     */
    text: {
      type: String,
      required: true,
    },
  },
  data: () => ({
    isHovered: false,
    isFocused: false,
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
        this.isFocused = false
      }
    },
    onFocusout(event) {
      if (!this.$el.contains(event.relatedTarget)) {
        this.isFocused = false
      }
    },
    onFocus() {
      this.isFocused = true
    },
  },
}

export default Dropdown
</script>

<style lang="scss">
.navbar-dropdown:not(.visible) {
  /* Accessible VisuallyHidden styles taken from @wordpress/components. Allows these components to be accessibly hidden from sight while still being focusable */
  clip: rect(1px, 1px, 1px, 1px);
  height: 1px;
  left: -2px;
  margin: 0;
  overflow: hidden;
  padding: 0;
  position: absolute;
  width: 1px;
  z-index: 99999;
}
</style>
