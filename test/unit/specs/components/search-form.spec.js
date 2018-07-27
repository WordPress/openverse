import Vue from 'vue';
import SearchForm from '@/components/SearchForm';

describe('SearchForm.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(SearchForm);
    const vm = new Constructor().$mount();
  });
});
