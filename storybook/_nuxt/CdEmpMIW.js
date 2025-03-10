import{h as a}from"./53SD24Bo.js";import{a as T,m as I,f as D}from"./D6RfD4r0.js";import{I as d}from"./f6gYKWT5.js";import{_ as p}from"./gJS8MC28.js";import"./RQxsyxdU.js";import"./BbcJJQG6.js";import"./BW6nfHgy.js";import"./BjsSTAr7.js";import"./Cai0IfA4.js";import"./7RO02bE1.js";import"./CGjrUY8T.js";import"./DXnxRZFx.js";import"./B2IxrC02.js";import"./CLVl6rL5.js";import"./C-ucudUc.js";import"./BALwooav.js";import"./CxEt8vcx.js";import"./BnJv8bNI.js";import"./okj3qyDJ.js";import"./ByZ6H8Q9.js";import"./oAL5f6fw.js";import"./B7ZxQ_gM.js";import"./CGdESDy3.js";import"./C4QhmNcb.js";import"./CxzE6WfI.js";import"./BsOxdBIg.js";import"./DhTbjJlp.js";import"./Duw_lVTV.js";import"./DLCnOpdB.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="24fbfcb4-8768-4bad-ab74-2a778455f3df",e._sentryDebugIdIdentifier="sentry-dbid-24fbfcb4-8768-4bad-ab74-2a778455f3df")}catch{}})();const re={title:"Components/VHeader/VFilterButton",component:p,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},w=e=>({components:{VFilterButton:p},setup(){const t=T();t.setSearchType(d);function n(x){t.clearFilters();const h=[...I[d]];let r=0,s=1;for(let m=0;m<x;m++){const l=h[s];t.toggleFilter({filterType:l,codeIdx:r}),r+=1,D[l].length===r&&(s+=1,r=0)}}return n(e.appliedFilters),()=>a("div",{class:"flex"},[a("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[a(p,e)])])}}),o={render:w.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},i={render:w.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var f,c,u;o.parameters={...o.parameters,docs:{...(f=o.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
