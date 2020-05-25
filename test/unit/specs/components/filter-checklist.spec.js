import FilterChecklist from '@/components/Filters/FilterChecklist';
import render from '../../test-utils/render';

describe('FilterChecklist', () => {
  let options = {};
  let props = null;

  const eventData = {
    target: {
      id: 'foo',
    },
  };

  beforeEach(() => {
    props = {
      options: [{ code: 'foo', name: 'bar', checked: false }],
      title: 'Foo',
      filterType: 'bar',
      disabled: false,
    };
    options = {
      propsData: props,
      mocks: {
        $store: {
          state: {
            experiments: [{
              name: 'filter_visibility_experiment',
              case: 'filters_collapsed_experiment',
            }],
          },
        },
      },
    };
  });

  it('should render correct contents', () => {
    const wrapper = render(FilterChecklist, options);
    expect(wrapper.find('.filters').vm).toBeDefined();
  });

  it('should render filter visibility toggle button', () => {
    const wrapper = render(FilterChecklist, options);
    expect(wrapper.find('.filter-visibility-toggle').element).toBeDefined();
  });

  it('should not render filter visibility toggle button with expanded ab test', () => {
    options.mocks.$store.state.experiments[0].case = 'filters_expanded_experiment';
    const wrapper = render(FilterChecklist, options);
    expect(wrapper.find('.filter-visibility-toggle').element).not.toBeDefined();
  });

  it('visibility toggle button should be in collapsed state by default', () => {
    const wrapper = render(FilterChecklist, options);
    expect(wrapper.find('.angle-down').element).toBeDefined();
  });

  it('shows checklist when visibility toggle button clicked', () => {
    const wrapper = render(FilterChecklist, options);
    wrapper.find('.filter-visibility-toggle').trigger('click');
    expect(wrapper.find('.filter-checkbox').element).toBeDefined();
    expect(wrapper.find('.angle-up').element).toBeDefined(); // toggle image should point up now
  });

  it('shows checklist with expanded ab test', () => {
    options.mocks.$store.state.experiments[0].case = 'filters_expanded_experiment';
    const wrapper = render(FilterChecklist, options);
    expect(wrapper.find('.filter-checkbox').element).toBeDefined();
  });

  it('hides checklist when visibility toggle button pressed twice', () => {
    const wrapper = render(FilterChecklist, options);
    wrapper.find('.filter-visibility-toggle').trigger('click'); // should open
    wrapper.find('.filter-visibility-toggle').trigger('click'); // should close
    expect(wrapper.find('.angle-down').element).toBeDefined();
  });

  it('should call filterChanged event', () => {
    const mockMethods = {
      onValueChange: jest.fn(),
    };
    options.methods = mockMethods;

    const wrapper = render(FilterChecklist, options);
    wrapper.setData({ filtersVisible: true });

    const checkbox = wrapper.find('.filter-checkbox');
    expect(checkbox.element).toBeDefined();

    checkbox.trigger('change');
    expect(options.methods.onValueChange).toHaveBeenCalled();
  });

  it('should emit filterChanged event', () => {
    const wrapper = render(FilterChecklist, options);
    wrapper.vm.onValueChange(eventData);
    expect(wrapper.emitted().filterChanged).toBeTruthy();
  });
});
