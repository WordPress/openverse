import{V as r}from"./C9zp20eV.js";import"./DHOw7aFH.js";import{h as i}from"./Bf-AzR54.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},s=new e.Error().stack;s&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[s]="ebe9e028-7903-45a0-8b09-facd7c77af6f",e._sentryDebugIdIdentifier="sentry-dbid-ebe9e028-7903-45a0-8b09-facd7c77af6f")}catch{}})();const f={title:"Components/VSnackbar",component:r,argTypes:{size:{options:["large","small"],control:"radio"},isVisible:{control:"boolean"}}},n={name:"Primary",args:{size:"small",isVisible:!0},render:e=>({components:{VSnackbar:r},setup(){return()=>i(r,{...e,style:{display:e.isVisible?"block":"none"}},{default:()=>"Snackbar message"})}})};var a,o,t;n.parameters={...n.parameters,docs:{...(a=n.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
