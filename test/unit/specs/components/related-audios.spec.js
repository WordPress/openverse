import RelatedAudios from '~/components/AudioDetails/Related'
import render from '../../test-utils/render'
import { createLocalVue, mount } from '@vue/test-utils'
import Vuex from 'vuex'
import VueI18n from 'vue-i18n'

const audioResults = [{ id: 'audio1' }, { id: 'audio2' }]
const serviceMock = {
  getRelatedMedia: jest.fn(() =>
    Promise.resolve({ data: { results: audioResults } })
  ),
}

const localVue = createLocalVue()
localVue.use(Vuex)
localVue.use(VueI18n)
localVue.prototype.$nuxt = {
  nbFetching: 0,
}

const doRender = async () => {
  return render(
    RelatedAudios,
    {
      localVue,
      propsData: { audioId: 'foo', service: serviceMock },
      mocks: { $fetchState: { pending: false, error: null, timestamp: null } },
      stubs: { LoadingIcon: true, AudioTrack: true },
    },
    mount
  )
}

describe('RelatedAudios', () => {
  it('should render content when finished loading related audios', async () => {
    const wrapper = await doRender()

    const header = wrapper.find('h4').text()
    expect(header).toEqual('audio-details.related-audios')

    const audioTracks = wrapper.findAll('audiotrack-stub')
    expect(audioTracks.length).toEqual(audioResults.length)

    expect(serviceMock.getRelatedMedia).toHaveBeenCalledTimes(1)
  })
})
