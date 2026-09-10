import{h as i}from"./DwwldUEF.js";import{V as r}from"./BXlqTUHv.js";import"./CWoQmekT.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},s=new e.Error().stack;s&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[s]="97778fc9-4c6b-49ac-9ea5-872a9bcf6676",e._sentryDebugIdIdentifier="sentry-dbid-97778fc9-4c6b-49ac-9ea5-872a9bcf6676")}catch{}})();const u={title:"Components/VSnackbar",component:r,argTypes:{size:{options:["large","small"],control:"radio"},isVisible:{control:"boolean"}}},n={name:"Primary",args:{size:"small",isVisible:!0},render:e=>({components:{VSnackbar:r},setup(){return()=>i(r,{...e,style:{display:e.isVisible?"block":"none"}},{default:()=>"Snackbar message"})}})};var a,o,t;n.parameters={...n.parameters,docs:{...(a=n.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
}`,...(t=(o=n.parameters)==null?void 0:o.docs)==null?void 0:t.source}}};const f=["Primary"];export{n as Primary,f as __namedExportsOrder,u as default};
