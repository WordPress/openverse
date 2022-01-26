import { ref, computed } from '@nuxtjs/composition-api'

import VModal from '~/components/VModal/VModal.vue'
import VModalTarget from '~/components/VModal/VModalTarget.vue'
import VButton from '~/components/VButton.vue'
import VPopover from '~/components/VPopover/VPopover.vue'

export default {
  component: VModal,
  title: 'Components/VModal',
  argTypes: {
    hideOnEsc: 'boolean',
    hideOnClickOutside: 'boolean',
    autoFocusOnShow: 'boolean',
    autoFocusOnHide: 'boolean',
    label: 'text',
    labelledBy: 'text',
    useCustomInitialFocus: {
      type: 'boolean',
      default: false,
    },
  },
}

const DefaultStory = (args, { argTypes }) => ({
  template: `
    <div>
      <VModal v-bind="$props" :initial-focus-element="resolvedInitialFocusElement">
        <template #trigger="{ a11yProps, visible }">
          <VButton v-bind="a11yProps">{{ visible ? 'Modal open' : 'Modal closed' }}</VButton>
        </template>

        <div class="p-4">
          This is some modal 1 content, blah blah blah.

          <VPopover>
            <template #trigger="{ a11yProps, visible }">
              <VButton v-bind="a11yProps">{{ visible ? 'Close popover' : 'Open popover' }}</VButton>
            </template>

            <div class="px-2">
              This is popover content! Woohoo! I'm inside a modal!!! Wow!!!
            </div>
          </VPopover>

          <!-- Lots of bogus stuff to test scrolling -->

          <p class="pt-5">
            Polymer is a Javascript NoSQL database. Passport. JavaScript web apps. Compiler is a JavaScript is a Web pages frequently do this usage are: Loading new objects. 2D graphics within the majority of desktop applications built on data to make things accessible to represent the browser which it has since been standardized specification. Test-Driven Development. WebGL is said to pages and out, resizing them, etc. Scripts are not include any I/O, such a tool to be isomorphic when its code and display dates and display animated 3D. C. Factory Pattern is a way for Behaviour-Driven Development. API for Behaviour-Driven Development. JSX is a design. Ionic is a class to its own build system and MongoDB is a multi-paradigm language, supporting object-oriented, imperative, and it changes in C. Redux is a swiss army knife, focusing on the Module Pattern is a Web form to make sure that gets called immediately but does not include any I/O, such as API for Babel is supported by caching the revealing module loader using observable streams.
          </p>

          <button type="button" ref="initialFocusElement">A focusable element that doesn't come first in the modal content</button>

          <p>
            PostCSS is a HTML5 mobile applications. Bluebird is a simple, pluggable static type checker, designed for browser is a task runner aiming at explaining the server. Native development. Patterns is a framework for dynamic web. Flux is a swiss army knife, focusing on Node. Wide Web analytics, ad tracking, personalization or included from development environment, simplifying a JavaScript implementation in Java. Mediator Pattern is used in and media queries. CommonJS is a structural framework based on the server via Ajax is a language name, syntax, and simple words. LocalForage is a popular browsers share support for most common use of one of deployment-ready files from HTML pages, also be used in the server. Arity is a JavaScript engine. AngularJS is a library for asynchronous HTTP requests for other projects like Node. VMs and the three core technologies of their containing scope. Hoisting is an API that allow programs and feature-rich client-side behavior to add client-side library for Node. Redux is by Nitobi. Rhino, like SpiderMonkey, is a Node.
          </p>
        </div>
      </VModal>

      <p>Intermediary content. Inspect me to observe the modal rendering in the target element instead of inline (which would be <em>before</em> this element in the DOM rather than after it)</p>

      <!-- Lots of bogus stuff to test scrolling -->

      <hr />

      <p>
        Polymer is a Javascript NoSQL database. Passport. JavaScript web apps. Compiler is a JavaScript is a Web pages frequently do this usage are: Loading new objects. 2D graphics within the majority of desktop applications built on data to make things accessible to represent the browser which it has since been standardized specification. Test-Driven Development. WebGL is said to pages and out, resizing them, etc. Scripts are not include any I/O, such a tool to be isomorphic when its code and display dates and display animated 3D. C. Factory Pattern is a way for Behaviour-Driven Development. API for Behaviour-Driven Development. JSX is a design. Ionic is a class to its own build system and MongoDB is a multi-paradigm language, supporting object-oriented, imperative, and it changes in C. Redux is a swiss army knife, focusing on the Module Pattern is a Web form to make sure that gets called immediately but does not include any I/O, such as API for Babel is supported by caching the revealing module loader using observable streams.
      </p>

      <p>
        PostCSS is a HTML5 mobile applications. Bluebird is a simple, pluggable static type checker, designed for browser is a task runner aiming at explaining the server. Native development. Patterns is a framework for dynamic web. Flux is a swiss army knife, focusing on Node. Wide Web analytics, ad tracking, personalization or included from development environment, simplifying a JavaScript implementation in Java. Mediator Pattern is used in and media queries. CommonJS is a structural framework based on the server via Ajax is a language name, syntax, and simple words. LocalForage is a popular browsers share support for most common use of one of deployment-ready files from HTML pages, also be used in the server. Arity is a JavaScript engine. AngularJS is a library for asynchronous HTTP requests for other projects like Node. VMs and the three core technologies of their containing scope. Hoisting is an API that allow programs and feature-rich client-side behavior to add client-side library for Node. Redux is by Nitobi. Rhino, like SpiderMonkey, is a Node.
      </p>

      <p>
        Polymer is a Javascript NoSQL database. Passport. JavaScript web apps. Compiler is a JavaScript is a Web pages frequently do this usage are: Loading new objects. 2D graphics within the majority of desktop applications built on data to make things accessible to represent the browser which it has since been standardized specification. Test-Driven Development. WebGL is said to pages and out, resizing them, etc. Scripts are not include any I/O, such a tool to be isomorphic when its code and display dates and display animated 3D. C. Factory Pattern is a way for Behaviour-Driven Development. API for Behaviour-Driven Development. JSX is a design. Ionic is a class to its own build system and MongoDB is a multi-paradigm language, supporting object-oriented, imperative, and it changes in C. Redux is a swiss army knife, focusing on the Module Pattern is a Web form to make sure that gets called immediately but does not include any I/O, such as API for Babel is supported by caching the revealing module loader using observable streams.
      </p>

      <p>
        PostCSS is a HTML5 mobile applications. Bluebird is a simple, pluggable static type checker, designed for browser is a task runner aiming at explaining the server. Native development. Patterns is a framework for dynamic web. Flux is a swiss army knife, focusing on Node. Wide Web analytics, ad tracking, personalization or included from development environment, simplifying a JavaScript implementation in Java. Mediator Pattern is used in and media queries. CommonJS is a structural framework based on the server via Ajax is a language name, syntax, and simple words. LocalForage is a popular browsers share support for most common use of one of deployment-ready files from HTML pages, also be used in the server. Arity is a JavaScript engine. AngularJS is a library for asynchronous HTTP requests for other projects like Node. VMs and the three core technologies of their containing scope. Hoisting is an API that allow programs and feature-rich client-side behavior to add client-side library for Node. Redux is by Nitobi. Rhino, like SpiderMonkey, is a Node.
      </p>

      <VModalTarget />
    </div>
  `,
  components: { VButton, VModal, VModalTarget, VPopover },
  props: Object.keys(argTypes),
  setup(props) {
    const initialFocusElement = ref()

    const resolvedInitialFocusElement = computed(() =>
      props.useCustomInitialFocus ? initialFocusElement.value : undefined
    )

    return { initialFocusElement, resolvedInitialFocusElement }
  },
})

export const Default = DefaultStory.bind({})
Default.args = {}
