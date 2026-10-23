import{h as p}from"./DmrXErv4.js";import{a as T,m as I,f as D}from"./Boj1x2qa.js";import{I as d}from"./BWJ9rAf_.js";import{_ as a}from"./BfcJYpOG.js";import"./Cre_5D1H.js";import"./P7ZX4TMp.js";import"./D8RLh9Dr.js";import"./DFZUF_34.js";import"./B3KNKrKa.js";import"./BxtqxG2r.js";import"./D7WD_DXd.js";import"./D_KYnWat.js";import"./wMBvb-CP.js";import"./CdQaOBNt.js";import"./C7sHCGoX.js";import"./B_dsH32H.js";import"./CEG4L8Wc.js";import"./CT8Zrxvs.js";import"./DzAq6MI-.js";import"./BRHrr7ck.js";import"./Bpr67t9y.js";import"./DWRfakdt.js";import"./CCN4kZnP.js";import"./Bn7RUpRV.js";import"./OMXwMIS8.js";import"./rMKLwKwR.js";import"./Dv0Nl23j.js";import"./DhTbjJlp.js";import"./DMHhTBZb.js";import"./D5Za6x0E.js";import"./Dx-3nI8A.js";import"./CJ7FTku9.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="1718bef4-1b74-42e5-8477-19224180b8e0",e._sentryDebugIdIdentifier="sentry-dbid-1718bef4-1b74-42e5-8477-19224180b8e0")}catch{}})();const oe={title:"Components/VHeader/VFilterButton",component:a,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},w=e=>({components:{VFilterButton:a},setup(){const t=T();t.setSearchType(d);function n(x){t.clearFilters();const h=[...I[d]];let r=0,s=1;for(let m=0;m<x;m++){const l=h[s];t.toggleFilter({filterType:l,codeIdx:r}),r+=1,D[l].length===r&&(s+=1,r=0)}}return n(e.appliedFilters),()=>p("div",{class:"flex"},[p("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[p(a,e)])])}}),o={render:w.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},i={render:w.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var c,f,u;o.parameters={...o.parameters,docs:{...(c=o.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
}`,...(g=(y=i.parameters)==null?void 0:y.docs)==null?void 0:g.source}}};const ie=["Default","WithTextLabel"];export{o as Default,i as WithTextLabel,ie as __namedExportsOrder,oe as default};
