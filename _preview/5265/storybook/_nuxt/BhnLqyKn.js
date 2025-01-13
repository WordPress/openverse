import{h as d}from"./DwwldUEF.js";import"./CjQ0HQF0.js";import{_ as a}from"./CU_z6qsI.js";import"../sb-preview/runtime.js";import"./Bu-vEs7l.js";import"./Dwl_h6Xz.js";import"./D9b6d0V7.js";import"./DhTbjJlp.js";import"./Ct9P1Zdp.js";import"./Bl4H7SX1.js";import"./DZZ1Fr_1.js";import"./rq0rg1X-.js";import"./B67cIdux.js";import"./Cqs9wCPQ.js";import"./BufT_yKp.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="7b74b2fc-be0b-4e20-9604-0bd51488a68e",e._sentryDebugIdIdentifier="sentry-dbid-7b74b2fc-be0b-4e20-9604-0bd51488a68e")}catch{}})();const l=["info","success","warning","error"],E={title:"Components/VNotificationBanner",component:a,argTypes:{sNature:{control:"select",options:[...l]},sVariant:{control:"select",options:["regular","dark"]},onClose:{action:"close"}},args:{sNature:"info",sVariant:"regular",id:"banner"}},f="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec nec justo eget felis facilisis fermentum.",p={render:e=>({components:{VNotificationBanner:a},setup(){return()=>d(a,{...e,variant:e.sVariant,nature:e.sNature},{default:()=>f})}})},r={...p,name:"Default",args:{sNature:"success",sVariant:"regular"}},t={...p,name:"Dark",args:{sNature:"info",sVariant:"dark"}};var s,o,i;r.parameters={...r.parameters,docs:{...(s=r.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    sNature: "success",
    sVariant: "regular"
  }
}`,...(i=(o=r.parameters)==null?void 0:o.docs)==null?void 0:i.source}}};var c,m,u;t.parameters={...t.parameters,docs:{...(c=t.parameters)==null?void 0:c.docs,source:{originalSource:`{
  ...Template,
  name: "Dark",
  args: {
    sNature: "info",
    sVariant: "dark"
  }
}`,...(u=(m=t.parameters)==null?void 0:m.docs)==null?void 0:u.source}}};const S=["Default","Dark"];export{t as Dark,r as Default,S as __namedExportsOrder,E as default};
