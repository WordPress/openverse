import{h as p}from"./53SD24Bo.js";import"./_bbq3c9C.js";import{_ as a}from"./2brFhQpd.js";import"../sb-preview/runtime.js";import"./dvXbmdTd.js";import"./ivjvpZKc.js";import"./DjsporFN.js";import"./DhTbjJlp.js";import"./xQ8_qGND.js";import"./DlboKt2a.js";import"./Di7dAt70.js";import"./B9k6C3Hw.js";import"./BOewZ2sR.js";import"./D2GrBf-6.js";import"./B_-6Taiq.js";import"./CH5-dTGy.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="3da14a54-b0fd-4b38-bff9-7366d0fdbc8d",e._sentryDebugIdIdentifier="sentry-dbid-3da14a54-b0fd-4b38-bff9-7366d0fdbc8d")}catch{}})();const f=["info","success","warning","error"],S={title:"Components/VNotificationBanner",component:a,argTypes:{sNature:{control:"select",options:[...f]},sVariant:{control:"select",options:["regular","dark"]},onClose:{action:"close"}},args:{sNature:"info",sVariant:"regular",id:"banner"}},l="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec justo eget felis facilisis fermentum.",u={render:e=>({components:{VNotificationBanner:a},setup(){return()=>p(a,{...e,variant:e.sVariant,nature:e.sNature},{default:()=>l})}})},r={...u,name:"Default",args:{sNature:"success",sVariant:"regular"}},t={...u,name:"Dark",args:{sNature:"info",sVariant:"dark"}};var s,o,i;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    sNature: "success",
    sVariant: "regular"
  }
}`,...(i=(o=r.parameters)==null?void 0:o.docs)==null?void 0:i.source}}};var c,m,d;t.parameters={...t.parameters,docs:{...(c=t.parameters)==null?void 0:c.docs,source:{originalSource:`{
  ...Template,
  name: "Dark",
  args: {
    sNature: "info",
    sVariant: "dark"
  }
}`,...(d=(m=t.parameters)==null?void 0:m.docs)==null?void 0:d.source}}};const j=["Default","Dark"];export{t as Dark,r as Default,j as __namedExportsOrder,S as default};
