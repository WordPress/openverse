import Vue from 'vue';
import SearchGridCell from '@/components/SearchGridCell';

describe('SearchGridCell.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(SearchGridCell);
    const vm = new Constructor().$mount();
  });
});
