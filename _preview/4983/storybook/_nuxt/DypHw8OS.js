import{V as n}from"./Cv7kj0Ot.js";import{h as t}from"./B18F2_lz.js";import"./DlAUqK2U.js";const c={title:"Components/VSnackbar",component:n,argTypes:{size:{options:["large","small"],control:"radio"},isVisible:{control:"boolean"}}},e={name:"Primary",args:{size:"small",isVisible:!0},render:r=>({components:{VSnackbar:n},setup(){return()=>t(n,{...r,style:{display:r.isVisible?"block":"none"}},{default:()=>"Snackbar message"})}})};var s,a,o;e.parameters={...e.parameters,docs:{...(s=e.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(o=(a=e.parameters)==null?void 0:a.docs)==null?void 0:o.source}}};const p=["Primary"];export{e as Primary,p as __namedExportsOrder,c as default};
