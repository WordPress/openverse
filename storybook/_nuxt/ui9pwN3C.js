import{i as t}from"./vQCScaZm.js";import{g as c}from"./DdMEaL1I.js";import{V as s,g as r}from"./Ds-vKKn_.js";import{u}from"./Daug3kJj.js";import{_ as l}from"./4Ti8BhRx.js";import{u as f}from"./BbpI8HCW.js";import"./D0ww02ZN.js";import"./CRWjC3CT.js";import"./DrNtRFwM.js";import"./B4Enkrnr.js";import"./Cy2QxSWR.js";import"./DGLF--vo.js";import"./CVtkxrq9.js";import"./BpA1-2Lw.js";import"./PbhuxOhq.js";import"./CFMQYC2y.js";import"./BeeEOwoo.js";import"./BGZSGO9i.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./BtCJ4zBB.js";import"./CM40ytJp.js";import"./DQnMOLSw.js";import"./Cl5peGfr.js";import"./CAYEskQw.js";import"./CQ1rVe0p.js";import"./BOX21o1p.js";import"./Xs_VBmP5.js";import"./BOiuNSD_.js";import"./BK2iIHTq.js";import"./Dt-H8hG_.js";import"./Cv8aVtrP.js";import"./BSEdKPgk.js";const e=c({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),g={render:d=>({template:`
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
  `,components:{VMetadata:s,VLanguageSelect:l},setup(){u().$patch({providers:{audio:[{source_name:e.source}],image:[{source_name:t.source}]},sourceNames:{audio:[e.source],image:[t.source]}});const o=f({useScope:"global"}),n=[{metadata:r(t,o,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:r(e,o),media:e}];return{args:d,data:n}}})},W={title:"Components/VMediaInfo/VMetadata",component:s},a={...g,name:"VMetadata"};var i,m,p;a.parameters={...a.parameters,docs:{...(i=a.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(m=a.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};const X=["Default"];export{a as Default,X as __namedExportsOrder,W as default};
