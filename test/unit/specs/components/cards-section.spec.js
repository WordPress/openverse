import Vue from 'vue';
import CardSection from '@/components/CardsSection';

describe('CardSection.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(CardSection);
    const vm = new Constructor().$mount();
  });
});
