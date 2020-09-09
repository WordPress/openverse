<template>
  <tooltip :tooltip="tooltip" tooltip-position="top">
    <span title="tooltip">
      <img class="help-icon" src="~/assets/help_icon.svg" alt="tooltip" />
    </span>
  </tooltip>
</template>

<script>
import Tooltip from '@/components/Tooltip'

export default {
  name: 'HelpTooltip',
  components: {
    Tooltip,
  },
  props: ['tooltip'],
}
</script>

<style lang="scss" scoped>
@import '../styles/photodetails.scss';
</style>
