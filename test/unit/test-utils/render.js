/* eslint-disable no-param-reassign */
import Puex from 'puex';
import { shallowMount, createLocalVue } from '@vue/test-utils';
import sampleStore from '../sampleStore/';

const localVue = createLocalVue();
localVue.use(Puex);

const render = (Component, options = { localVue }) => {
  if (!options.store) {
    const store = new Puex(sampleStore);
    options.store = store;
  }

  return shallowMount(Component, options);
};

export default render;
