import{h as i}from"./DmrXErv4.js";import{V as r}from"./CD3pE_mK.js";import"./Cre_5D1H.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},s=new e.Error().stack;s&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[s]="c136b6fc-f499-4069-a06d-7cec708db4fc",e._sentryDebugIdIdentifier="sentry-dbid-c136b6fc-f499-4069-a06d-7cec708db4fc")}catch{}})();const f={title:"Components/VSnackbar",component:r,argTypes:{size:{options:["large","small"],control:"radio"},isVisible:{control:"boolean"}}},n={name:"Primary",args:{size:"small",isVisible:!0},render:e=>({components:{VSnackbar:r},setup(){return()=>i(r,{...e,style:{display:e.isVisible?"block":"none"}},{default:()=>"Snackbar message"})}})};var a,o,t;n.parameters={...n.parameters,docs:{...(a=n.parameters)==null?void 0:a.docs,source:{originalSource:`{
  name: "Primary",
  args: {
    size: "small",
    isVisible: true
  },
  render: args => ({
    components: {
      VSnackbar
    },
    setup() {
      return () => h(VSnackbar, {
        ...args,
        style: {
          display: args.isVisible ? "block" : "none"
        }
      }, {
        default: () => "Snackbar message"
      });
    }
  })
}`,...(t=(o=n.parameters)==null?void 0:o.docs)==null?void 0:t.source}}};const u=["Primary"];export{n as Primary,u as __namedExportsOrder,f as default};
