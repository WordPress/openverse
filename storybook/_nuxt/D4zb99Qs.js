import{h as r}from"./DmrXErv4.js";import{W as y}from"./DSgSzK8z.js";import{_ as n}from"./7ji7nyEP.js";import{V as a}from"./Cw6R_86C.js";import"./Ceavzuo-.js";import"./CdX5GYQk.js";import"./qy-jYTsH.js";import"./BayljJpb.js";import"./DhTbjJlp.js";import"./_fZwI_6s.js";import"./Bp0tQXh7.js";import"./DoeNFUMW.js";import"./DjlphFtq.js";import"./BUYfIans.js";import"./BxtqxG2r.js";import"./FWiT1Y5Q.js";import"./Dbo3V4Mp.js";import"./Dp2jPxn_.js";import"./BS_ZT77X.js";import"./C_FySRQg.js";import"./DzAq6MI-.js";import"./CS1FkDVx.js";import"./D5Za6x0E.js";import"./Dx-3nI8A.js";import"./CJ7FTku9.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},c=new e.Error().stack;c&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[c]="e4b4da07-4ca8-47f4-b04f-1f64af93a61c",e._sentryDebugIdIdentifier="sentry-dbid-e4b4da07-4ca8-47f4-b04f-1f64af93a61c")}catch{}})();const N={title:"Components/VCheckbox",component:n,decorators:[y],args:{id:"default",name:"Code is Poetry",value:"codeIsPoetry",checked:!1,isSwitch:!1},argTypes:{onChange:{action:"change"}}},g={render:e=>({components:{VCheckbox:n},setup(){return()=>r(n,e,{default:()=>e.name})}})},t={...g,name:"Default"},o={...g,name:"Switch",args:{isSwitch:!0}},s={name:"License Checkbox",render:e=>({components:{VCheckbox:n,VLicense:a},setup(){return()=>r("fieldset",{},[r("legend",{},"License"),r(n,{...e,class:"mb-4"},[r(a,{license:"by-nc",class:"me-4"})])])}}),args:{id:"cc-by",name:"license",value:"cc-by",checked:!0}};var i,m,p;t.parameters={...t.parameters,docs:{...(i=t.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "Default"
}`,...(p=(m=t.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};var d,l,u;o.parameters={...o.parameters,docs:{...(d=o.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Switch",
  args: {
    isSwitch: true
  }
}`,...(u=(l=o.parameters)==null?void 0:l.docs)==null?void 0:u.source}}};var f,h,b;s.parameters={...s.parameters,docs:{...(f=s.parameters)==null?void 0:f.docs,source:{originalSource:`{
  name: "License Checkbox",
  render: args => ({
    components: {
      VCheckbox,
      VLicense
    },
    setup() {
      return () => h("fieldset", {}, [h("legend", {}, "License"), h(VCheckbox, {
        ...args,
        class: "mb-4"
      }, [h(VLicense, {
        license: "by-nc",
        class: "me-4"
      })])]);
    }
  }),
  args: {
    id: "cc-by",
    name: "license",
    value: "cc-by",
    checked: true
  }
}`,...(b=(h=s.parameters)==null?void 0:h.docs)==null?void 0:b.source}}};const Q=["Default","Switch","LicenseCheckbox"];export{t as Default,s as LicenseCheckbox,o as Switch,Q as __namedExportsOrder,N as default};
