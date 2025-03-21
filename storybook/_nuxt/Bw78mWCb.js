import{h as a}from"./53SD24Bo.js";import{a as T,m as I,f as D}from"./Dy4Kknks.js";import{I as d}from"./BMTpeGZl.js";import{_ as p}from"./C6zS6Ru5.js";import"./DBIAFgjH.js";import"./Bji7sDXf.js";import"./CErlnN7q.js";import"./D_Aw-xVi.js";import"./qH-7fQ0Y.js";import"./7RO02bE1.js";import"./CPPXHlee.js";import"./DnIg5T83.js";import"./DJCDDsZ8.js";import"./B5GQZ6KW.js";import"./DQdiNp-F.js";import"./DiSpNEja.js";import"./BL5vD3y7.js";import"./CLb7Coka.js";import"./okj3qyDJ.js";import"./BwPl7lue.js";import"./CBc_U4V9.js";import"./Bb2yh_vr.js";import"./BYpqqPRZ.js";import"./BRl0LMB0.js";import"./BNCCbueK.js";import"./DuKV0Hy2.js";import"./DhTbjJlp.js";import"./DWqKvFOC.js";import"./B9Cuo1Ro.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="24fbfcb4-8768-4bad-ab74-2a778455f3df",e._sentryDebugIdIdentifier="sentry-dbid-24fbfcb4-8768-4bad-ab74-2a778455f3df")}catch{}})();const re={title:"Components/VHeader/VFilterButton",component:p,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},w=e=>({components:{VFilterButton:p},setup(){const t=T();t.setSearchType(d);function n(x){t.clearFilters();const h=[...I[d]];let r=0,s=1;for(let m=0;m<x;m++){const l=h[s];t.toggleFilter({filterType:l,codeIdx:r}),r+=1,D[l].length===r&&(s+=1,r=0)}}return n(e.appliedFilters),()=>a("div",{class:"flex"},[a("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[a(p,e)])])}}),o={render:w.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},i={render:w.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var f,c,u;o.parameters={...o.parameters,docs:{...(f=o.parameters)==null?void 0:f.docs,source:{originalSource:`{
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
