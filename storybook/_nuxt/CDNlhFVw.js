import{a as w,m as F,f as V}from"./CnOclXYv.js";import{I as s}from"./CRWjC3CT.js";import{_ as a}from"./CBRNGQjT.js";import{h as i}from"./B18F2_lz.js";import"./CFYL8r3V.js";import"./CnlriU-7.js";import"./9FKpjZKd.js";import"./CFMQYC2y.js";import"./Dt-H8hG_.js";import"./CTON8dBl.js";import"./DSIC1A7N.js";import"./Cpj98o6Y.js";import"./Ci7G4jyV.js";import"./5GeBose5.js";import"./D0ww02ZN.js";import"./CCI1_F0E.js";import"./CKrGKsKZ.js";import"./CVtkxrq9.js";import"./Xs_VBmP5.js";import"./lEZE49IS.js";import"./BSEdKPgk.js";import"./BY12SjvE.js";import"./BOX21o1p.js";import"./_dzyiV2Y.js";import"./BC9BnLXc.js";import"./BdoT2ima.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./YMBo1cBL.js";const $={title:"Components/VHeader/VFilterButton",component:a,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},g=p=>({components:{VFilterButton:a},setup(){const o=w();o.setSearchType(s);function y(T){o.clearFilters();const h=[...F[s]];let e=0,m=1;for(let n=0;n<T;n++){let l=h[m];o.toggleFilter({filterType:l,codeIdx:e}),e+=1,V[l].length===e&&(m+=1,e=0)}}return y(p.appliedFilters),()=>i("div",{class:"flex"},[i("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[i(a,p)])])}}),t={render:g.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},r={render:g.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var d,c,f;t.parameters={...t.parameters,docs:{...(d=t.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
