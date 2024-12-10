import{a as w,m as F,f as V}from"./Bmz-fAWG.js";import{I as l}from"./CRWjC3CT.js";import{_ as a}from"./B5BhXDGY.js";import{h as i}from"./D21kBugn.js";import"./KtaE-n0E.js";import"./CTON8dBl.js";import"./Dt-H8hG_.js";import"./DmWT6tLV.js";import"./C66CHCZN.js";import"./Ci7G4jyV.js";import"./gmSLTnsl.js";import"./D0ww02ZN.js";import"./Xs_VBmP5.js";import"./JYtQN4fY.js";import"./BQsRc94L.js";import"./CszWEYKx.js";import"./CVtkxrq9.js";import"./Cpj98o6Y.js";import"./D4JcsNEP.js";import"./BOX21o1p.js";import"./C_KzvzgK.js";import"./K-1Rbgrz.js";import"./CFMQYC2y.js";import"./DzUJZ0J9.js";import"./DEweiwTv.js";import"./DlAUqK2U.js";import"./D8Wpa1kZ.js";import"./DyBDyB1K.js";import"./C1YDwe8s.js";const $={title:"Components/VHeader/VFilterButton",component:a,argTypes:{pressed:{type:"boolean"},appliedFilters:{type:"number"},disabled:{type:"boolean"},onToggle:{action:"toggle"}}},g=p=>({components:{VFilterButton:a},setup(){const o=w();o.setSearchType(l);function y(T){o.clearFilters();const h=[...F[l]];let e=0,m=1;for(let n=0;n<T;n++){const s=h[m];o.toggleFilter({filterType:s,codeIdx:e}),e+=1,V[s].length===e&&(m+=1,e=0)}}return y(p.appliedFilters),()=>i("div",{class:"flex"},[i("div",{id:"wrapper",class:"px-4 h-16 bg-surface flex align-center justify-center"},[i(a,p)])])}}),t={render:g.bind({}),name:"Default",parameters:{viewport:{defaultViewport:"lg"}}},r={render:g.bind({}),name:"With text label",parameters:{viewport:{defaultViewport:"xl"}}};var c,d,f;t.parameters={...t.parameters,docs:{...(c=t.parameters)==null?void 0:c.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "Default",
  parameters: {
    viewport: {
      defaultViewport: "lg"
    }
  }
}`,...(f=(d=t.parameters)==null?void 0:d.docs)==null?void 0:f.source}}};var u,x,b;r.parameters={...r.parameters,docs:{...(u=r.parameters)==null?void 0:u.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "With text label",
  parameters: {
    viewport: {
      defaultViewport: "xl"
    }
  }
}`,...(b=(x=r.parameters)==null?void 0:x.docs)==null?void 0:b.source}}};const ee=["Default","WithTextLabel"];export{t as Default,r as WithTextLabel,ee as __namedExportsOrder,$ as default};
