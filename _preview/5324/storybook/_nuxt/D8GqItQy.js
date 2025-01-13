import{W as y}from"./CEIUB3th.js";import{_ as n}from"./BU978w3n.js";import{V as a}from"./DALxtJ8x.js";import"./BQ2uyTwE.js";import{h as r}from"./ueSFnAt6.js";import"./dNCV0R31.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DDGXuWLI.js";import"./DhTbjJlp.js";import"./BS4Oynt6.js";import"./EYmIadoG.js";import"./DHgysDkh.js";import"./CG6WIkST.js";import"./BEqh9yyh.js";import"./cS2ccka-.js";import"./5wCrcqN-.js";import"./BKGw6EjD.js";import"./DSEYgdJX.js";import"./C4YS0AQy.js";import"./C_jCWbT6.js";import"./DzAq6MI-.js";import"./DLWVrS0P.js";import"./rltOz0pP.js";import"./cXVshVQU.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},c=new e.Error().stack;c&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[c]="575820f6-7055-4bc4-aaa1-f1bb8cb89d31",e._sentryDebugIdIdentifier="sentry-dbid-575820f6-7055-4bc4-aaa1-f1bb8cb89d31")}catch{}})();const Q={title:"Components/VCheckbox",component:n,decorators:[y],args:{id:"default",name:"Code is Poetry",value:"codeIsPoetry",checked:!1,isSwitch:!1},argTypes:{onChange:{action:"change"}}},g={render:e=>({components:{VCheckbox:n},setup(){return()=>r(n,e,{default:()=>e.name})}})},t={...g,name:"Default"},o={...g,name:"Switch",args:{isSwitch:!0}},s={name:"License Checkbox",render:e=>({components:{VCheckbox:n,VLicense:a},setup(){return()=>r("fieldset",{},[r("legend",{},"License"),r(n,{...e,class:"mb-4"},[r(a,{license:"by-nc",class:"me-4"})])])}}),args:{id:"cc-by",name:"license",value:"cc-by",checked:!0}};var i,m,p;t.parameters={...t.parameters,docs:{...(i=t.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "Default"
}`,...(p=(m=t.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};var d,l,u;o.parameters={...o.parameters,docs:{...(d=o.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Switch",
  args: {
    isSwitch: true
  }
}`,...(u=(l=o.parameters)==null?void 0:l.docs)==null?void 0:u.source}}};var b,f,h;s.parameters={...s.parameters,docs:{...(b=s.parameters)==null?void 0:b.docs,source:{originalSource:`{
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
}`,...(h=(f=s.parameters)==null?void 0:f.docs)==null?void 0:h.source}}};const R=["Default","Switch","LicenseCheckbox"];export{t as Default,s as LicenseCheckbox,o as Switch,R as __namedExportsOrder,Q as default};
