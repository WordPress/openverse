import Vue from 'vue';
import NavSection from '@/components/NavSection';

describe('NavSection.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(NavSection);
    const vm = new Constructor().$mount();
  });
});
