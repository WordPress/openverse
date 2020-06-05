<template>
    <div class="locale">
      Languages available
      <div class="control has-icons-left">
        <div class="select">
          <select v-model="$i18n.locale">
            <option v-for="locale in locales" :key="locale.name" :value="locale.name">
              {{locale.eng}} - {{locale.native}}
            </option>
          </select>
        </div>
        <div class="icon globe is-small is-left">
            <i class="icon globe">locale</i>
        </div>
      </div>
    </div>
</template>

<script>
import getlocales from '../utils/locales';

export default {
  name: 'locale-selector',
  data() {
    return {
      locales: getlocales(),
      currentLanguage: 'English',
    };
  },
};
</script>

<style lang="scss" scoped>
.icon i {
  padding-top: 0.75rem;
  padding-left: 1.25rem;
}
</style>
