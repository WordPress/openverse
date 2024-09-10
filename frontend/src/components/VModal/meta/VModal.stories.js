import { h, ref, computed } from "vue"

import VModal from "~/components/VModal/VModal.vue"
import VButton from "~/components/VButton.vue"
import VPopover from "~/components/VPopover/VPopover.vue"

export default {
  title: "Components/VModal",
  component: VModal,
  argTypes: {
    hideOnEsc: { control: { type: "boolean" } },

    hideOnClickOutside: { control: { type: "boolean" } },

    autoFocusOnShow: { control: { type: "boolean" } },

    autoFocusOnHide: { control: { type: "boolean" } },

    label: { control: { type: "text" } },

    labelledBy: { control: { type: "text" } },

    useCustomInitialFocus: { control: { type: "boolean" } },
  },
}

const Template = (args) => ({
  components: { VButton, VModal, VPopover },
  setup() {
    const initialFocusElement = ref()
    const resolvedInitialFocusElement = computed(() =>
      args.useCustomInitialFocus ? initialFocusElement.value : undefined
    )

    return () =>
      h("div", [
        h(
          VModal,
          {
            ...args,
            initialFocusElement: resolvedInitialFocusElement.value,
            id: "modal-story",
          },
          {
            trigger: ({ a11yProps, visible }) =>
              h(
                VButton,
                {
                  variant: "bordered-gray",
                  size: "medium",
                  ...a11yProps,
                },
                () => (visible ? "Modal open" : "Modal closed")
              ),
            default: () =>
              h("div", { class: "p-4" }, [
                "This is some modal 1 content, blah etc.",
                h(
                  VPopover,
                  {
                    id: "popover-in-modal",
                  },
                  {
                    trigger: ({ a11yProps, visible }) =>
                      h(
                        VButton,
                        {
                          variant: "bordered-gray",
                          size: "medium",
                          ...a11yProps,
                        },
                        () => (visible ? "Close popover" : "Open popover")
                      ),
                    default: () =>
                      h(
                        "div",
                        { class: "px-2" },
                        "This is popover content! Woohoo! I'm inside a modal! Wow!"
                      ),
                  }
                ),
                h(
                  "p",
                  { class: "pt-5" },
                  "Polymer is a Javascript NoSQL database. Passport. JavaScript web apps. Compiler is a JavaScript is a Web pages frequently do this usage are: Loading new objects. 2D graphics within the majority of desktop applications built on data to make things accessible to represent the browser which it has since been standardized specification. Test-Driven Development. WebGL is said to pages and out, resizing them, etc. Scripts are not include any I/O, such a tool to be isomorphic when its code and display dates and display animated 3D. C. Factory Pattern is a way for Behaviour-Driven Development. API for Behaviour-Driven Development. JSX is a design. Ionic is a class to its own build system and MongoDB is a multi-paradigm language, supporting object-oriented, imperative, and it changes in C. Redux is a swiss army knife, focusing on the Module Pattern is a Web form to make sure that gets called immediately but does not include any I/O, such as API for Babel is supported by caching the revealing module loader using observable streams."
                ),
                h(
                  "button",
                  {
                    type: "button",
                    ref: initialFocusElement,
                  },
                  "A focusable element that doesn't come first in the modal content"
                ),
                h(
                  "p",
                  "PostCSS is a HTML5 mobile applications. Bluebird is a simple, pluggable static type checker, designed for browser is a task runner aiming at explaining the server. Native development. Patterns is a framework for dynamic web. Flux is a swiss army knife, focusing on Node. Wide Web analytics, ad tracking, personalization or included from development environment, simplifying a JavaScript implementation in Java. Mediator Pattern is used in and media queries. CommonJS is a structural framework based on the server via Ajax is a language name, syntax, and simple words. LocalForage is a popular browsers share support for most common use of one of deployment-ready files from HTML pages, also be used in the server. Arity is a JavaScript engine. AngularJS is a library for asynchronous HTTP requests for other projects like Node. VMs and the three core technologies of their containing scope. Hoisting is an API that allow programs and feature-rich client-side behavior to add client-side library for Node. Redux is by Nitobi. Rhino, like SpiderMonkey, is a Node."
                ),
              ]),
          }
        ),
        h("p", [
          "Intermediary content. Inspect me to observe the modal rendering in the target element instead of inline (which would be ",
          h("em", "before"),
          " this element in the DOM rather than after it)",
        ]),
        h("hr"),
        h(
          "p",
          "Polymer is a Javascript NoSQL database. Passport. JavaScript web apps. Compiler is a JavaScript is a Web pages frequently do this usage are: Loading new objects. 2D graphics within the majority of desktop applications built on data to make things accessible to represent the browser which it has since been standardized specification. Test-Driven Development. WebGL is said to pages and out, resizing them, etc. Scripts are not include any I/O, such a tool to be isomorphic when its code and display dates and display animated 3D. C. Factory Pattern is a way for Behaviour-Driven Development. API for Behaviour-Driven Development. JSX is a design. Ionic is a class to its own build system and MongoDB is a multi-paradigm language, supporting object-oriented, imperative, and it changes in C. Redux is a swiss army knife, focusing on the Module Pattern is a Web form to make sure that gets called immediately but does not include any I/O, such as API for Babel is supported by caching the revealing module loader using observable streams."
        ),
        h(
          "p",
          "PostCSS is a HTML5 mobile applications. Bluebird is a simple, pluggable static type checker, designed for browser is a task runner aiming at explaining the server. Native development. Patterns is a framework for dynamic web. Flux is a swiss army knife, focusing on Node. Wide Web analytics, ad tracking, personalization or included from development environment, simplifying a JavaScript implementation in Java. Mediator Pattern is used in and media queries. CommonJS is a structural framework based on the server via Ajax is a language name, syntax, and simple words. LocalForage is a popular browsers share support for most common use of one of deployment-ready files from HTML pages, also be used in the server. Arity is a JavaScript engine. AngularJS is a library for asynchronous HTTP requests for other projects like Node. VMs and the three core technologies of their containing scope. Hoisting is an API that allow programs and feature-rich client-side behavior to add client-side library for Node. Redux is by Nitobi. Rhino, like SpiderMonkey, is a Node."
        ),
        h(
          "p",
          "Polymer is a Javascript NoSQL database. Passport. JavaScript web apps. Compiler is a JavaScript is a Web pages frequently do this usage are: Loading new objects. 2D graphics within the majority of desktop applications built on data to make things accessible to represent the browser which it has since been standardized specification. Test-Driven Development. WebGL is said to pages and out, resizing them, etc. Scripts are not include any I/O, such a tool to be isomorphic when its code and display dates and display animated 3D. C. Factory Pattern is a way for Behaviour-Driven Development. API for Behaviour-Driven Development. JSX is a design. Ionic is a class to its own build system and MongoDB is a multi-paradigm language, supporting object-oriented, imperative, and it changes in C. Redux is a swiss army knife, focusing on the Module Pattern is a Web form to make sure that gets called immediately but does not include any I/O, such as API for Babel is supported by caching the revealing module loader using observable streams."
        ),
        h(
          "p",
          "PostCSS is a HTML5 mobile applications. Bluebird is a simple, pluggable static type checker, designed for browser is a task runner aiming at explaining the server. Native development. Patterns is a framework for dynamic web. Flux is a swiss army knife, focusing on Node. Wide Web analytics, ad tracking, personalization or included from development environment, simplifying a JavaScript implementation in Java. Mediator Pattern is used in and media queries. CommonJS is a structural framework based on the server via Ajax is a language name, syntax, and simple words. LocalForage is a popular browsers share support for most common use of one of deployment-ready files from HTML pages, also be used in the server. Arity is a JavaScript engine. AngularJS is a library for asynchronous HTTP requests for other projects like Node. VMs and the three core technologies of their containing scope. Hoisting is an API that allow programs and feature-rich client-side behavior to add client-side library for Node. Redux is by Nitobi. Rhino, like SpiderMonkey, is a Node."
        ),
        h("div", { id: "teleports" }),
      ])
  },
})

export const Default = {
  render: Template.bind({}),
  name: "Default",

  args: {
    useCustomInitialFocus: false,
  },
}
