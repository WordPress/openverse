import{h as d}from"./53SD24Bo.js";import"./ey6Ec0eW.js";import{_ as t}from"./Bf7twscG.js";import"../sb-preview/runtime.js";import"./CCSsdpEp.js";import"./BxMTa-Rq.js";import"./B7QaUHa9.js";import"./DhTbjJlp.js";import"./hoiiP6gd.js";import"./DtcCBiui.js";import"./DzXFAWuk.js";import"./D6STwiFZ.js";import"./Cw5DoNPI.js";import"./Bdn_xeD6.js";import"./C81jPTEF.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="3a1fe4e1-1aa4-48e7-bc88-5c6944079af1",e._sentryDebugIdIdentifier="sentry-dbid-3a1fe4e1-1aa4-48e7-bc88-5c6944079af1")}catch{}})();const f=["info","success","warning","error"],E={title:"Components/VNotificationBanner",component:t,argTypes:{sNature:{control:"select",options:[...f]},sVariant:{control:"select",options:["regular","dark"]},onClose:{action:"close"}},args:{sNature:"info",sVariant:"regular",id:"banner"}},l="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec justo eget felis facilisis fermentum.",p={render:e=>({components:{VNotificationBanner:t},setup(){return()=>d(t,{...e,variant:e.sVariant,nature:e.sNature},{default:()=>l})}})},r={...p,name:"Default",args:{sNature:"success",sVariant:"regular"}},a={...p,name:"Dark",args:{sNature:"info",sVariant:"dark"}};var s,o,i;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
