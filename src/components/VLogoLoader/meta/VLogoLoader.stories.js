import VLogoLoader from '~/components/VLogoLoader/VLogoLoader'

export default {
  component: VLogoLoader,
  title: 'Components/VLogoLoader',
  argTypes: {
    status: {
      default: 'idle',
      options: ['loading', 'idle'],
      control: { type: 'radio' },
    },
  },
}

const SimpleLoaderStory = (_, { argTypes }) => ({
  props: Object.keys(argTypes),
  template: `
    <div>
      <VLogoLoader v-bind="$props" />
      <p>Remember to test with the <code class="inline p-0"><pre class="inline bg-light-gray p-0 m-0 leading-normal">prefers-reduced-motion</pre></code> media query. You can find instructions for doing so in Firefox <a href="https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion#user_preferences">here.</a></p>
    </div>
  `,
  components: { VLogoLoader },
})

export const Default = SimpleLoaderStory.bind({})
Default.args = {
  status: 'idle',
}

export const Loading = SimpleLoaderStory.bind({})
Loading.args = {
  status: 'loading',
  loadingLabel: 'Loading images',
}

const LinkWrappedLoaderStory = (_, { argTypes }) => ({
  props: Object.keys(argTypes),
  template: `
    <a class="focus:outline-none focus:ring focus:ring-offset-2 focus:ring-pink inline-block" href='https://wordpress.org/openverse'>
      <VLogoLoader v-bind="$props" />
    </a>
  `,
  components: { VLogoLoader },
})

export const LinkWrapped = LinkWrappedLoaderStory.bind({})
LinkWrappedLoaderStory.args = {
  status: 'idle',
  loadingLabel: 'Loading images',
}
