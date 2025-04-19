import{h as d}from"./53SD24Bo.js";import"./DxXQfK2h.js";import{_ as t}from"./DGrn0I-H.js";import"../sb-preview/runtime.js";import"./CO_nLv6a.js";import"./DY7Jae7t.js";import"./1q_AdtTO.js";import"./DhTbjJlp.js";import"./m1m5Z0c3.js";import"./Do357AjE.js";import"./Ab-gfhxw.js";import"./BfmvDfJj.js";import"./COHSvtot.js";import"./CbQ_U0bA.js";import"./GK6z1vC-.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="3a1fe4e1-1aa4-48e7-bc88-5c6944079af1",e._sentryDebugIdIdentifier="sentry-dbid-3a1fe4e1-1aa4-48e7-bc88-5c6944079af1")}catch{}})();const f=["info","success","warning","error"],E={title:"Components/VNotificationBanner",component:t,argTypes:{sNature:{control:"select",options:[...f]},sVariant:{control:"select",options:["regular","dark"]},onClose:{action:"close"}},args:{sNature:"info",sVariant:"regular",id:"banner"}},l="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec justo eget felis facilisis fermentum.",p={render:e=>({components:{VNotificationBanner:t},setup(){return()=>d(t,{...e,variant:e.sVariant,nature:e.sNature},{default:()=>l})}})},r={...p,name:"Default",args:{sNature:"success",sVariant:"regular"}},a={...p,name:"Dark",args:{sNature:"info",sVariant:"dark"}};var s,o,i;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    sNature: "success",
    sVariant: "regular"
  }
}`,...(i=(o=r.parameters)==null?void 0:o.docs)==null?void 0:i.source}}};var c,m,u;a.parameters={...a.parameters,docs:{...(c=a.parameters)==null?void 0:c.docs,source:{originalSource:`{
  ...Template,
  name: "Dark",
  args: {
    sNature: "info",
    sVariant: "dark"
  }
}`,...(u=(m=a.parameters)==null?void 0:m.docs)==null?void 0:u.source}}};const S=["Default","Dark"];export{a as Dark,r as Default,S as __namedExportsOrder,E as default};
