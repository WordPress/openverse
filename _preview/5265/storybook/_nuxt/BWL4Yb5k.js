import{a as u}from"./BS9R2VWD.js";import{V as o}from"./D-UB-1q8.js";import{h as c}from"./D21kBugn.js";import"./BMFse2nb.js";import"./x16T20Hu.js";import"./D9Dxf084.js";import"./DzUJZ0J9.js";import"./DEweiwTv.js";import"./CFMQYC2y.js";import"./DlAUqK2U.js";import"./D4JcsNEP.js";import"./BOX21o1p.js";import"./DmWT6tLV.js";import"./C_KzvzgK.js";import"./K-1Rbgrz.js";import"./JYtQN4fY.js";const E={title:"Components/Audio track/Audio control",component:o,argTypes:{status:{options:u,control:"select"},size:{options:["small","medium","large"],control:"select"},onToggle:{action:"toggle"}}},p={render:l=>({components:{VAudioControl:o},setup(){return()=>c(o,l)}})},e={...p,name:"Default",args:{status:"playing",size:"large"}},t={...p,name:"Disabled",args:{disabled:!0,status:"playing",size:"medium"}};var r,a,s;e.parameters={...e.parameters,docs:{...(r=e.parameters)==null?void 0:r.docs,source:{originalSource:`{
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
