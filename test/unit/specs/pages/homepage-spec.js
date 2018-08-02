import Vue from 'vue';
import Homepage from '@/pages/HomePage';

describe('Homepage.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(Homepage);
    const vm = new Constructor().$mount();
  });
});
