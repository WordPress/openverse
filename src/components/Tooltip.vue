<template>
  <div
    v-if="visible"
    :tooltip="tooltip"
    :tooltip-position="tooltipPosition"
    class="help-tooltip"
    @click="toggleVisibility"
    @keyup.enter="toggleVisibility"
  >
    <slot />
  </div>
  <div v-else @click="toggleVisibility" @keyup.enter="toggleVisibility">
    <slot />
  </div>
</template>

<script>
export default {
  name: 'Tooltip',
  props: ['tooltip', 'tooltipPosition'],
  data: () => ({
    visible: false,
  }),
  methods: {
    toggleVisibility() {
      this.visible = !this.visible
    },
  },
}
</script>

<style lang="scss" scoped>
div {
  position: relative;
  display: inline-block;
  cursor: pointer;
}
[tooltip]::before {
  content: '';
  position: absolute;
  top: -6px;
  left: 50%;
  transform: translateX(-50%);
  border-width: 4px 6px 0 6px;
  border-style: solid;
  border-color: rgba(0, 0, 0, 0.9) transparent transparent transparent;
  z-index: 99;
}

[tooltip-position='left']::before {
  left: 0%;
  top: 50%;
  margin-left: -12px;
  transform: translatey(-50%) rotate(-90deg);
}
[tooltip-position='top']::before {
  left: 50%;
}
[tooltip-position='buttom']::before {
  top: 100%;
  margin-top: 8px;
  transform: translateX(-50%) translatey(-100%) rotate(-180deg);
}
[tooltip-position='right']::before {
  left: 100%;
  top: 50%;
  margin-left: 1px;
  transform: translatey(-50%) rotate(90deg);
}

[tooltip]::after {
  content: attr(tooltip);
  position: absolute;
  left: 50%;
  top: -6px;
  transform: translateX(-50%) translateY(-100%);
  background: rgba(0, 0, 0, 0.9);
  text-align: center;
  color: #fff;
  padding: 4px 2px;
  font-size: 12px;
  min-width: 300px;
  border-radius: 5px;
  pointer-events: none;
  padding: 4px 4px;
  z-index: 99;
}

[tooltip-position='left']::after {
  left: 0%;
  top: 50%;
  margin-left: -8px;
  transform: translateX(-100%) translateY(-50%);
}
[tooltip-position='top']::after {
  left: 50%;
}
[tooltip-position='buttom']::after {
  top: 100%;
  margin-top: 8px;
  transform: translateX(-50%) translateY(0%);
}
[tooltip-position='right']::after {
  left: 100%;
  top: 50%;
  margin-left: 8px;
  transform: translateX(0%) translateY(-50%);
}
</style>
