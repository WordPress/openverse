import Vue from 'vue';
import SearchGrid from '@/components/SearchGrid';

describe('SearchGrid.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(SearchGrid);
    const vm = new Constructor().$mount();
  });
});
