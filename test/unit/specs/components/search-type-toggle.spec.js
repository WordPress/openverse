import Vue from 'vue'
import SearchTypeToggle from '~/components/SearchTypeToggle'
import { render, screen } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'

const TestWrapper = Vue.component('TestWrapper', {
  components: { SearchTypeToggle },
  data() {
    return { value: undefined }
  },
  template: `<SearchTypeToggle v-model="value" />`,
})

const getImageRadio = () => screen.getByText('hero.search-type.image')
const getAudioRadio = () => screen.getByText('hero.search-type.audio')

describe('SearchTypeToggle', () => {
  it('should default to image checked', () => {
    render(TestWrapper)
    const imageRadio = getImageRadio()
    const audioRadio = getAudioRadio()
    expect(imageRadio).toHaveAttribute('aria-checked', 'true')
    expect(audioRadio).not.toHaveAttribute('aria-checked')
  })

  it('should select the clicked search type', async () => {
    render(TestWrapper)
    await userEvent.click(getAudioRadio())
    expect(getImageRadio()).not.toHaveAttribute('aria-checked')
    expect(getAudioRadio()).toHaveAttribute('aria-checked', 'true')
  })
})
