import{u as c}from"./DKepsN1e.js";import{i as t}from"./vQCScaZm.js";import{g as u}from"./DdMEaL1I.js";import{V as s,g as r}from"./B887uWEI.js";import{u as l}from"./PgLs4BFy.js";import{_ as f}from"./DXmMC2T-.js";import"./BSEdKPgk.js";import"./lnpB3OcH.js";import"./D0ww02ZN.js";import"./CRWjC3CT.js";import"./Xs_VBmP5.js";import"./BNurbrIm.js";import"./D-c0xjtQ.js";import"./CFMQYC2y.js";import"./BsB6Edd_.js";import"./DToSwJe0.js";import"./CVtkxrq9.js";import"./BInFDkJi.js";import"./CtE17snF.js";import"./ZjNmaQpL.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./TZ8H9kUZ.js";import"./DyOEVqiO.js";import"./DQnMOLSw.js";import"./Do2yKSxf.js";import"./DuVMw8T-.js";import"./BvLt3-_D.js";import"./BOX21o1p.js";import"./wqDFrKMd.js";import"./CoPWYLvr.js";import"./Dt-H8hG_.js";import"./dxvBluQ8.js";const e=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),g={render:d=>({template:`
    <div class="flex flex-col gap-y-2">
      <VLanguageSelect />
      <section class="wrapper flex flex-col p-2 gap-y-2 bg-surface">
        <VMetadata
        v-for="datum in data"
        :key="datum.media.id"
        :metadata="datum.metadata"
        :media="datum.media"
        v-bind="datum"
        class="bg-default"/>
      </section>
    </div>
  `,components:{VMetadata:s,VLanguageSelect:f},setup(){l().$patch({providers:{audio:[{source_name:e.source}],image:[{source_name:t.source}]},sourceNames:{audio:[e.source],image:[t.source]}});const o=c({useScope:"global"}),n=[{metadata:r(t,o,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:r(e,o),media:e}];return{args:d,data:n}}})},W={title:"Components/VMediaInfo/VMetadata",component:s},a={...g,name:"VMetadata"};var i,m,p;a.parameters={...a.parameters,docs:{...(i=a.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(m=a.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};const X=["Default"];export{a as Default,X as __namedExportsOrder,W as default};
