import{a as T,m as I,f as D}from"./xNdBFmJU.js";import{I as d}from"./DqF6eGgl.js";import{_ as p}from"./Cuudky5l.js";import"./DUksCy1Q.js";import{h as a}from"./Bf-AzR54.js";import"./C91c9mPJ.js";import"./Ce-pb_5E.js";import"./CH1X1jge.js";import"./DekjSk5G.js";import"./B06Wl6je.js";import"./BkYjW3Tf.js";import"./Drofs-2p.js";import"./-xUPu9Rx.js";import"./y8WIPfCZ.js";import"./-W0rxRVk.js";import"./CQEj5Ugn.js";import"./DC3f6ECh.js";import"./qkf-DtgY.js";import"./DzAq6MI-.js";import"./DIrLFUJi.js";import"./CGo6q8cg.js";import"./Cf91XFr0.js";import"./CvkTs5vB.js";import"./8Pdn1Bl1.js";import"./CAhZsXLM.js";import"./BEmSFkVT.js";import"./DhTbjJlp.js";import"./BtRzq8b5.js";import"./FADBYOvo.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="88d29c54-88e5-46ce-8450-c4819e1dac58",e._sentryDebugIdIdentifier="sentry-dbid-88d29c54-88e5-46ce-8450-c4819e1dac58")}catch{}})();const te={title:"Components/VHeader/VFilterButton",component:p,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},w=e=>({components:{VFilterButton:p},setup(){const t=T();t.setSearchType(d);function n(x){t.clearFilters();const h=[...I[d]];let r=0,s=1;for(let l=0;l<x;l++){const m=h[s];t.toggleFilter({filterType:m,codeIdx:r}),r+=1,D[m].length===r&&(s+=1,r=0)}}return n(e.appliedFilters),()=>a("div",{class:"flex"},[a("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[a(p,e)])])}}),o={render:w.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},i={render:w.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var c,f,u;o.parameters={...o.parameters,docs:{...(c=o.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
