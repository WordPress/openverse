import{W as x}from"./DsElxYru.js";import"./DHOw7aFH.js";import{h as v}from"./Bf-AzR54.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="cc0bf71d-366e-48ef-a352-2ee5aa3cc8db",e._sentryDebugIdIdentifier="sentry-dbid-cc0bf71d-366e-48ef-a352-2ee5aa3cc8db")}catch{}})();const w={title:"Meta/Focus",decorators:[x]},l=e=>r=>({setup(){return()=>v("div",{class:`h-30 w-30 flex items-center justify-center ${e} ${r.classNames.join(" ")}`,"data-testid":"focus-target",tabindex:"0"},"Focus on me")}}),s={render:l("border border-disabled hover:border-hover").bind({}),name:"Slim transparent",args:{classNames:["focus-slim-tx"]}},a={render:l("bg-tertiary text-over-dark border border-tx").bind({}),name:"Slim filled",args:{classNames:["focus-slim-filled"]}},d={render:l("bg-primary text-over-dark").bind({}),name:"Slim filled borderless",args:{classNames:["focus-slim-borderless-filled"]}},o={render:l("bg-complementary text-default").bind({}),name:"Bold filled",args:{classNames:["focus-visible:focus-bold-filled"]}};var t,n,i;s.parameters={...s.parameters,docs:{...(t=s.parameters)==null?void 0:t.docs,source:{originalSource:`{
  render: GetTemplate("border border-disabled hover:border-hover").bind({}),
  name: "Slim transparent",
  args: {
    classNames: ["focus-slim-tx"]
  }
}`,...(i=(n=s.parameters)==null?void 0:n.docs)==null?void 0:i.source}}};var c,m,b;a.parameters={...a.parameters,docs:{...(c=a.parameters)==null?void 0:c.docs,source:{originalSource:`{
  render: GetTemplate("bg-tertiary text-over-dark border border-tx").bind({}),
  name: "Slim filled",
  args: {
    classNames: ["focus-slim-filled"]
  }
}`,...(b=(m=a.parameters)==null?void 0:m.docs)==null?void 0:b.source}}};var f,u,p;d.parameters={...d.parameters,docs:{...(f=d.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: GetTemplate("bg-primary text-over-dark").bind({}),
  name: "Slim filled borderless",
  args: {
    classNames: ["focus-slim-borderless-filled"]
  }
}`,...(p=(u=d.parameters)==null?void 0:u.docs)==null?void 0:p.source}}};var g,S,y;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
  render: GetTemplate("bg-complementary text-default").bind({}),
  name: "Bold filled",
  args: {
    classNames: ["focus-visible:focus-bold-filled"]
  }
}`,...(y=(S=o.parameters)==null?void 0:S.docs)==null?void 0:y.source}}};const B=["SlimTransparent","SlimFilled","SlimFilledBorderless","BoldFilled"];export{o as BoldFilled,a as SlimFilled,d as SlimFilledBorderless,s as SlimTransparent,B as __namedExportsOrder,w as default};
