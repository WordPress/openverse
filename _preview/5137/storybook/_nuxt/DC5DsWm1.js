import{a as u}from"./BS9R2VWD.js";import{V as o}from"./KPakBTOk.js";import{h as c}from"./-WkxctKM.js";import"./BPwGQkdi.js";import"./BxOnwPF8.js";import"./C0aPY4k7.js";import"./CVV9gpzL.js";import"./CuPsdpTl.js";import"./CFMQYC2y.js";import"./DlAUqK2U.js";import"./CmiN-34A.js";import"./8bxaQBfd.js";import"./DNZ0QEaN.js";import"./BOX21o1p.js";import"./BKKKF4W5.js";import"./BnDRGrsR.js";const E={title:"Components/Audio track/Audio control",component:o,argTypes:{status:{options:u,control:"select"},size:{options:["small","medium","large"],control:"select"},onToggle:{action:"toggle"}}},p={render:l=>({components:{VAudioControl:o},setup(){return()=>c(o,l)}})},e={...p,name:"Default",args:{status:"playing",size:"large"}},t={...p,name:"Disabled",args:{disabled:!0,status:"playing",size:"medium"}};var r,a,s;e.parameters={...e.parameters,docs:{...(r=e.parameters)==null?void 0:r.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    status: "playing",
    size: "large"
  }
}`,...(s=(a=e.parameters)==null?void 0:a.docs)==null?void 0:s.source}}};var n,i,m;t.parameters={...t.parameters,docs:{...(n=t.parameters)==null?void 0:n.docs,source:{originalSource:`{
  ...Template,
  name: "Disabled",
  args: {
    disabled: true,
    status: "playing",
    size: "medium"
  }
}`,...(m=(i=t.parameters)==null?void 0:i.docs)==null?void 0:m.source}}};const O=["Default","Disabled"];export{e as Default,t as Disabled,O as __namedExportsOrder,E as default};
