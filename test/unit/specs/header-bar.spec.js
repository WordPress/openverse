import Vue from 'vue';
import HeaderBar from '@/components/HeaderBar';

describe('Header.vue', () => {
  it('should render correct contents', () => {
    const Constructor = Vue.extend(HeaderBar);
    const vm = new Constructor().$mount();
    expect(vm.$el.querySelector('header h1').textContent)
      .toEqual('Share, Collaborate, Remix, Reuse');
  });
});
