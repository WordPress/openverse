import{V as r}from"./vICCtR36.js";import"./BQ2uyTwE.js";import{h as i}from"./ueSFnAt6.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},s=new e.Error().stack;s&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[s]="5a62e0eb-db47-4670-9932-61cd3d1dd2a8",e._sentryDebugIdIdentifier="sentry-dbid-5a62e0eb-db47-4670-9932-61cd3d1dd2a8")}catch{}})();const u={title:"Components/VSnackbar",component:r,argTypes:{size:{options:["large","small"],control:"radio"},isVisible:{control:"boolean"}}},n={name:"Primary",args:{size:"small",isVisible:!0},render:e=>({components:{VSnackbar:r},setup(){return()=>i(r,{...e,style:{display:e.isVisible?"block":"none"}},{default:()=>"Snackbar message"})}})};var a,o,t;n.parameters={...n.parameters,docs:{...(a=n.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
}`,...(t=(o=n.parameters)==null?void 0:o.docs)==null?void 0:t.source}}};const y=["Primary"];export{n as Primary,y as __namedExportsOrder,u as default};
