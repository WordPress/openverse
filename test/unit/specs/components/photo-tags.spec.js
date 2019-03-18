import PhotoTags from '@/components/PhotoTags';
import render from '../../test-utils/render';
import { SET_QUERY } from '@/store/mutation-types';

describe('PhotoTags', () => {
  let options = null;
  let props = null;

  beforeEach(() => {
    props = {
      tags: [
        {
          accuracy: 1,
          name: "foo",
          provider: "clarifai",
        },
        {
          accuracy: 1,
          name: "bar",
          provider: "foo",
        },
      ]
    };

    options = {
      propsData: props,
    };
  }); 
  
  it('should render correct contents when tags array is not empty', () => {
    const wrapper = render(PhotoTags, options);
    expect(wrapper.find('.photo_tags').element).toBeDefined();
    expect(wrapper.findAll('.photo_tag').length).toBe(2);
  }); 

  it('should render nothing when tags array is empty', () => {
    options.propsData.tags = [];
    const wrapper = render(PhotoTags, options);
    expect(wrapper.find('.photo_tags').element).toBeUndefined();
  });

  it('should render tags by clarifai section when atleast one tag provider is clarifai', () => {
    const wrapper = render(PhotoTags, options);
    expect(wrapper.find('.photo_tags-clarifai-badge').element).toBeDefined();
  });

  it('should not render tags by clarifai section when no tag is provided by clarifai', () => {
    options.propsData.tags[0].provider = 'foo';
    const wrapper = render(PhotoTags, options);
    expect(wrapper.find('.photo_tags-clarifai-badge').element).toBeUndefined();
  });

  it('it should render clarifai logo with a tag only if the tag provider is clarifai', () => {
    const wrapper = render(PhotoTags, options);
    const tagsArray = wrapper.findAll('.photo_tag');
    expect(tagsArray.at(0).find('.photo_tag-provider-badge').element).toBeDefined();
    expect(tagsArray.at(1).find('.photo_tag-provider-badge').element).toBeUndefined();
  });

  it('commits a mutation when a tag is clicked', () => {
    const storeMock = {
        commit: jest.fn()
    };
    const options = {
      propsData: {
        ...props,
      },
      mocks: {
        $store: storeMock,
      },
    };
   const wrapper = render(PhotoTags, options);
   wrapper.find('.photo_tag').trigger('click');
   const tagName = wrapper.find('.photo_tag').text()
   expect(storeMock.commit).toHaveBeenCalledWith(SET_QUERY, { query: { q: tagName }, shouldNavigate:true});
  });
});
