<template>
  <tooltip :tooltip="tooltip" tooltipPosition="top">
    <span title="tooltip">
      <img class="help-icon" src="../assets/help_icon.svg" alt="tooltip" />
    </span>
  </tooltip>
</template>

<script>
import Tooltip from '@/components/Tooltip'

export default {
  name: 'help-tooltip',
  props: ['tooltip'],
  components: {
    Tooltip,
  },
}
</script>

<style lang="scss" scoped>
@import '../styles/photodetails.scss';
</style>
