import Vue from 'vue';
import FooterSection from '@/components/FooterSection';

describe('FooterSection.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(FooterSection);
   	const vm = new Constructor().$mount();
  });
});
