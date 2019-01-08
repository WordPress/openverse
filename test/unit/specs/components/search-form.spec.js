import Vue from 'vue';
import SearchGridForm from '@/components/SearchGridForm';

describe('SearchGridForm.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(SearchGridForm);
    const vm = new Constructor().$mount();
  });
});
