<template>
  <div class="locale">
    {{ $t('hero.locale.label') }}
    <div class="control has-icons-left">
      <div class="select">
        <select v-model="$i18n.locale" @blur="setLocale($event)">
          <option
            v-for="locale in locales"
            :key="locale.name"
            :value="locale.name"
          >
            {{ locale.eng }} - {{ locale.native }}
          </option>
        </select>
      </div>
      <div class="icon globe is-small is-left">
        <i class="icon globe">{{ $t('hero.locale.icon') }}</i>
      </div>
    </div>
  </div>
</template>

<script>
import getlocales from '../utils/locales'

export default {
  name: 'LocaleSelector',
  data() {
    return {
      locales: getlocales(),
      currentLanguage: 'English',
    }
  },
  methods: {
    setLocale(event) {
      window.localStorage.setItem('locale', event.target.value)
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'bulma/sass/utilities/_all';

.icon i {
  padding-top: 0.75rem;
  padding-left: 1.25rem;
}

@include mobile {
  .locale {
    flex-direction: column;
    justify-content: center;
  }
}
</style>
