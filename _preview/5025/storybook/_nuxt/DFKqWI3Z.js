import{a as w,m as F,f as V}from"./BJ-KpVIG.js";import{I as s}from"./CRWjC3CT.js";import{_ as a}from"./YspSskTg.js";import{h as i}from"./lnpB3OcH.js";import"./BNurbrIm.js";import"./BInFDkJi.js";import"./BvLt3-_D.js";import"./CFMQYC2y.js";import"./Dt-H8hG_.js";import"./CTON8dBl.js";import"./CoPWYLvr.js";import"./Cpj98o6Y.js";import"./Ci7G4jyV.js";import"./PgLs4BFy.js";import"./D0ww02ZN.js";import"./wqDFrKMd.js";import"./DToSwJe0.js";import"./CVtkxrq9.js";import"./Xs_VBmP5.js";import"./DKepsN1e.js";import"./BSEdKPgk.js";import"./DuVMw8T-.js";import"./BOX21o1p.js";import"./CtE17snF.js";import"./D-c0xjtQ.js";import"./ZjNmaQpL.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./91sRmqhQ.js";const $={title:"Components/VHeader/VFilterButton",component:a,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},g=p=>({components:{VFilterButton:a},setup(){const o=w();o.setSearchType(s);function y(T){o.clearFilters();const h=[...F[s]];let e=0,m=1;for(let n=0;n<T;n++){let l=h[m];o.toggleFilter({filterType:l,codeIdx:e}),e+=1,V[l].length===e&&(m+=1,e=0)}}return y(p.appliedFilters),()=>i("div",{class:"flex"},[i("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[i(a,p)])])}}),t={render:g.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},r={render:g.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var d,c,f;t.parameters={...t.parameters,docs:{...(d=t.parameters)==null?void 0:d.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "Default",
  parameters: {
    viewport: {
      defaultViewport: "lg"
    }
  }
}`,...(f=(c=t.parameters)==null?void 0:c.docs)==null?void 0:f.source}}};var u,x,b;r.parameters={...r.parameters,docs:{...(u=r.parameters)==null?void 0:u.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "With text label",
  parameters: {
    viewport: {
      defaultViewport: "xl"
    }
  }
}`,...(b=(x=r.parameters)==null?void 0:x.docs)==null?void 0:b.source}}};const ee=["Default","WithTextLabel"];export{t as Default,r as WithTextLabel,ee as __namedExportsOrder,$ as default};
