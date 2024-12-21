import{a as T,m as I,f as D}from"./BxCgZ025.js";import{I as d}from"./CkK3diBk.js";import{_ as p}from"./DGGT3XJn.js";import"./D6xGyQxu.js";import{h as a}from"./Bf-AzR54.js";import"./BnJZTjE_.js";import"./CUyQTIYr.js";import"./BsG3jt0b.js";import"./CRElLIkf.js";import"./B06Wl6je.js";import"./C7lp-ITr.js";import"./BZTl3SGY.js";import"./SxvBqf-I.js";import"./BvQxCwAx.js";import"./Tu1w6jvB.js";import"./DBWmBUzF.js";import"./eAGCzEdq.js";import"./G0IPDLoE.js";import"./DzAq6MI-.js";import"./6ItBZc85.js";import"./v8hTCxed.js";import"./D3fY7LA9.js";import"./EvZx83Uz.js";import"./p8nc5Li4.js";import"./DmNhhvCU.js";import"./CO4aZKIX.js";import"./DhTbjJlp.js";import"./aBZnLbtd.js";import"./FADBYOvo.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="88d29c54-88e5-46ce-8450-c4819e1dac58",e._sentryDebugIdIdentifier="sentry-dbid-88d29c54-88e5-46ce-8450-c4819e1dac58")}catch{}})();const te={title:"Components/VHeader/VFilterButton",component:p,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},w=e=>({components:{VFilterButton:p},setup(){const t=T();t.setSearchType(d);function n(x){t.clearFilters();const h=[...I[d]];let r=0,s=1;for(let l=0;l<x;l++){const m=h[s];t.toggleFilter({filterType:m,codeIdx:r}),r+=1,D[m].length===r&&(s+=1,r=0)}}return n(e.appliedFilters),()=>a("div",{class:"flex"},[a("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[a(p,e)])])}}),o={render:w.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},i={render:w.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var c,f,u;o.parameters={...o.parameters,docs:{...(c=o.parameters)==null?void 0:c.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "Default",
  parameters: {
    viewport: {
      defaultViewport: "lg"
    }
  }
}`,...(u=(f=o.parameters)==null?void 0:f.docs)==null?void 0:u.source}}};var b,y,g;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "With text label",
  parameters: {
    viewport: {
      defaultViewport: "xl"
    }
  }
}`,...(g=(y=i.parameters)==null?void 0:y.docs)==null?void 0:g.source}}};const re=["Default","WithTextLabel"];export{o as Default,i as WithTextLabel,re as __namedExportsOrder,te as default};
