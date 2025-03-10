import{h as u}from"./53SD24Bo.js";import{a as c}from"./B6kCequ5.js";import{V as o}from"./CqanvgLS.js";import"./DgrDIC-J.js";import"./B6vXBV7d.js";import"./C715yFha.js";import"./f-66QnrL.js";import"./DhUVMU7d.js";import"./CJ-njDxe.js";import"./DhTbjJlp.js";import"./CKGOzHjv.js";import"./RmKinknp.js";import"./Dq1j0f_z.js";import"./Bm3FqArX.js";import"./BKOhH9JE.js";import"./DhLxMFu1.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},s=new e.Error().stack;s&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[s]="8b5decab-16b7-492b-9843-046d4d62498e",e._sentryDebugIdIdentifier="sentry-dbid-8b5decab-16b7-492b-9843-046d4d62498e")}catch{}})();const v={title:"Components/Audio track/Audio control",component:o,argTypes:{status:{options:c,control:"select"},size:{options:["small","medium","large"],control:"select"},onToggle:{action:"toggle"}}},l={render:e=>({components:{VAudioControl:o},setup(){return()=>u(o,e)}})},t={...l,name:"Default",args:{status:"playing",size:"large"}},r={...l,name:"Disabled",args:{disabled:!0,status:"playing",size:"medium"}};var a,n,i;t.parameters={...t.parameters,docs:{...(a=t.parameters)==null?void 0:a.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    status: "playing",
    size: "large"
  }
}`,...(i=(n=t.parameters)==null?void 0:n.docs)==null?void 0:i.source}}};var m,d,p;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Disabled",
  args: {
    disabled: true,
    status: "playing",
    size: "medium"
  }
}`,...(p=(d=r.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};const O=["Default","Disabled"];export{t as Default,r as Disabled,O as __namedExportsOrder,v as default};
