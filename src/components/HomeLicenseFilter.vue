<template>
  <div>
    <span>I want something I can</span>

    <div v-for="licenseType in licenseTypes">
      <label :for="licenseType.code">{{ licenseType.name }}</label>
      <input :id="licenseType.code"
              type="checkbox"
              :checked="licenseType.checked"
              @input="onFilterChanged(licenseType.code)" />
    </div>
  </div>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types';

export default {
  name: 'license-filter',
  methods: {
    onFilterChanged(code) {
      this.licenseTypes.forEach((lt) => {
        if (lt.code === code) {
          lt.checked = true;
        }
      });
      const filter = this.licenseTypes
        .filter(lt => lt.checked)
        .map(filterItem => filterItem.code)
        .join(',');

      this.$store.commit(SET_QUERY, {
        query: {
          lt: filter,
        },
      });
    },
  },
  data() {
    return {
      licenseTypes: [
        { code: 'commercial', name: 'Use for commercial purposes', checked: false },
        { code: 'modification', name: 'Modify or adapt', checked: false },
      ],
    };
  },
};
</script>

<style lang="scss" scoped>

</style>
