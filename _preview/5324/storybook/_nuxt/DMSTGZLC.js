import{a as T,m as I,f as D}from"./BKvBQNfv.js";import{I as d}from"./BUcLuzj5.js";import{_ as p}from"./tKxe0ima.js";import"./BQ2uyTwE.js";import{h as a}from"./ueSFnAt6.js";import"./BKGw6EjD.js";import"./D9PGBJDx.js";import"./CxIz9G_3.js";import"./DSEYgdJX.js";import"./cS2ccka-.js";import"./EYmIadoG.js";import"./nu0uObuU.js";import"./CP2tuLu8.js";import"./BXlC2Afm.js";import"./DHgysDkh.js";import"./C4YS0AQy.js";import"./5wCrcqN-.js";import"./C_jCWbT6.js";import"./DzAq6MI-.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./DDGXuWLI.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DhTbjJlp.js";import"./DqwLVH-w.js";import"./rltOz0pP.js";import"./cXVshVQU.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="184b524c-7ce9-4906-8bc8-7315a346e4f3",e._sentryDebugIdIdentifier="sentry-dbid-184b524c-7ce9-4906-8bc8-7315a346e4f3")}catch{}})();const re={title:"Components/VHeader/VFilterButton",component:p,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},w=e=>({components:{VFilterButton:p},setup(){const t=T();t.setSearchType(d);function n(x){t.clearFilters();const h=[...I[d]];let r=0,s=1;for(let m=0;m<x;m++){const l=h[s];t.toggleFilter({filterType:l,codeIdx:r}),r+=1,D[l].length===r&&(s+=1,r=0)}}return n(e.appliedFilters),()=>a("div",{class:"flex"},[a("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[a(p,e)])])}}),o={render:w.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},i={render:w.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var c,f,u;o.parameters={...o.parameters,docs:{...(c=o.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
}`,...(g=(y=i.parameters)==null?void 0:y.docs)==null?void 0:g.source}}};const oe=["Default","WithTextLabel"];export{o as Default,i as WithTextLabel,oe as __namedExportsOrder,re as default};
