import{h as a}from"./DwwldUEF.js";import{a as T,m as I,f as D}from"./Ds_kB4O7.js";import{I as d}from"./CAa63J2U.js";import{_ as p}from"./DPVVA9PQ.js";import"./CWoQmekT.js";import"./Z8zkSHZ1.js";import"./BAdCBbtP.js";import"./Dl1S6mqo.js";import"./TLA9Fm80.js";import"./Ck0CgHQL.js";import"./aHnQ5-ra.js";import"./ghAvikQd.js";import"./Bkc2CSET.js";import"./D8qJDlnG.js";import"./Cyc9srVp.js";import"./VcnMPoS3.js";import"./I6oWuQE1.js";import"./C8BbUAkk.js";import"./DzAq6MI-.js";import"./Dhs1Or-2.js";import"./CUvT7aun.js";import"./DqyB4W5h.js";import"./BtS8wA1z.js";import"./tAHCZdDM.js";import"./DoSYsHAz.js";import"./aezMCrU2.js";import"./DhTbjJlp.js";import"./g9Fv9Qqu.js";import"./D93TPuWH.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="24fbfcb4-8768-4bad-ab74-2a778455f3df",e._sentryDebugIdIdentifier="sentry-dbid-24fbfcb4-8768-4bad-ab74-2a778455f3df")}catch{}})();const re={title:"Components/VHeader/VFilterButton",component:p,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},w=e=>({components:{VFilterButton:p},setup(){const t=T();t.setSearchType(d);function n(x){t.clearFilters();const h=[...I[d]];let r=0,s=1;for(let m=0;m<x;m++){const l=h[s];t.toggleFilter({filterType:l,codeIdx:r}),r+=1,D[l].length===r&&(s+=1,r=0)}}return n(e.appliedFilters),()=>a("div",{class:"flex"},[a("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[a(p,e)])])}}),o={render:w.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},i={render:w.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var f,c,u;o.parameters={...o.parameters,docs:{...(f=o.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
