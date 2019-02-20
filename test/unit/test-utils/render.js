import Puex from 'puex';
import { shallowMount, createLocalVue } from '@vue/test-utils';
import sampleStore from '../sampleStore/';

const localVue = createLocalVue();
localVue.use(Puex);

const render = (Component, props) => {
  const store = new Puex(sampleStore);

  return shallowMount(Component, { store, localVue, propsData: props });
};

export default render;
