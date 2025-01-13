import{h as a}from"./DwwldUEF.js";import{a as T,m as I,f as D}from"./DyntKXIc.js";import{I as d}from"./DyjmqLvs.js";import{_ as p}from"./DVoZ7Hye.js";import"./BKd6qjwJ.js";import"./B_JavP0r.js";import"./TJSYFxys.js";import"./DXt3Hw-9.js";import"./DrQM85Nc.js";import"./Ck0CgHQL.js";import"./DeIUwsAH.js";import"./Bc_6hboB.js";import"./BJKkpTjt.js";import"./DIa_evZO.js";import"./D5nIdk7e.js";import"./DEzOOYTC.js";import"./BA2RD0IG.js";import"./BwtrEtqR.js";import"./DzAq6MI-.js";import"./R_--_Flr.js";import"./Duzn9Bak.js";import"./B7G-YaxP.js";import"./Efi66Qad.js";import"./DjJGxhuO.js";import"./D318SDY2.js";import"./BMyQprRt.js";import"./DhTbjJlp.js";import"./2U_rrX29.js";import"./D93TPuWH.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="24fbfcb4-8768-4bad-ab74-2a778455f3df",e._sentryDebugIdIdentifier="sentry-dbid-24fbfcb4-8768-4bad-ab74-2a778455f3df")}catch{}})();const re={title:"Components/VHeader/VFilterButton",component:p,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},w=e=>({components:{VFilterButton:p},setup(){const t=T();t.setSearchType(d);function n(x){t.clearFilters();const h=[...I[d]];let r=0,s=1;for(let m=0;m<x;m++){const l=h[s];t.toggleFilter({filterType:l,codeIdx:r}),r+=1,D[l].length===r&&(s+=1,r=0)}}return n(e.appliedFilters),()=>a("div",{class:"flex"},[a("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[a(p,e)])])}}),o={render:w.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},i={render:w.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var f,c,u;o.parameters={...o.parameters,docs:{...(f=o.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "Default",
  parameters: {
    viewport: {
      defaultViewport: "lg"
    }
  }
}`,...(u=(c=o.parameters)==null?void 0:c.docs)==null?void 0:u.source}}};var b,y,g;i.parameters={...i.parameters,docs:{...(b=i.parameters)==null?void 0:b.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "With text label",
  parameters: {
    viewport: {
      defaultViewport: "xl"
    }
  }
}`,...(g=(y=i.parameters)==null?void 0:y.docs)==null?void 0:g.source}}};const oe=["Default","WithTextLabel"];export{o as Default,i as WithTextLabel,oe as __namedExportsOrder,re as default};
