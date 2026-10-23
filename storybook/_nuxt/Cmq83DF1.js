import{h as e}from"./DmrXErv4.js";import{V as t,_ as s}from"./aHqcmVPk.js";import{_ as n}from"./C5WoR0kV.js";import"./Ceavzuo-.js";import"./CVvkZ7Vc.js";import"./0xbGHjBU.js";import"./lCCmDL6e.js";import"./Dp2jPxn_.js";import"./CtkidDXQ.js";import"./CMZS2cOm.js";import"./BayljJpb.js";import"./BS_ZT77X.js";import"./Ck0gvfbg.js";import"./CdX5GYQk.js";import"./qy-jYTsH.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var a=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},l=new a.Error().stack;l&&(a._sentryDebugIds=a._sentryDebugIds||{},a._sentryDebugIds[l]="eb4cd705-e382-4473-85f9-aef8bf72203f",a._sentryDebugIdIdentifier="sentry-dbid-eb4cd705-e382-4473-85f9-aef8bf72203f")}catch{}})();const f={render:a=>({components:{VTabs:s,VTabPanel:n,VTab:t},setup(){return()=>e(s,{...a},{tabs:()=>[e(t,{id:"1"},{default:()=>"Tab1"}),e(t,{id:"2"},{default:()=>"Tab2"}),e(t,{id:"3"},{default:()=>"Tab3"})],default:()=>[e(n,{id:"1"},{default:()=>"Page 1 content"}),e(n,{id:"2"},{default:()=>"Page 2 content"}),e(n,{id:"3"},{default:()=>"Page 3 content"})]})}})},O={component:s,subcomponents:{VTabPanel:n,VTab:t},title:"Components/VTabs",argTypes:{variant:{options:["bordered","plain"],control:{type:"radio"}},onClose:{action:"close"},onChange:{action:"change"}}},r={...f,name:"Default",args:{label:"Default tabs story",selectedId:"1"}},o={...f,name:"Manual plain tabs",args:{label:"Manual plain tabs",selectedId:"1",manual:!0,variant:"plain"}};var i,d,p;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    label: "Default tabs story",
    selectedId: "1"
  }
}`,...(p=(d=r.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};var m,u,c;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Manual plain tabs",
  args: {
    label: "Manual plain tabs",
    selectedId: "1",
    manual: true,
    variant: "plain"
  }
}`,...(c=(u=o.parameters)==null?void 0:u.docs)==null?void 0:c.source}}};const $=["Default","ManualPlainTabs"];export{r as Default,o as ManualPlainTabs,$ as __namedExportsOrder,O as default};
