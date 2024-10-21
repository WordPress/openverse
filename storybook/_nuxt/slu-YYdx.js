import{u as c}from"./lEZE49IS.js";import{i as t}from"./vQCScaZm.js";import{g as u}from"./DdMEaL1I.js";import{V as s,g as r}from"./DDKKvX_L.js";import{u as l}from"./5GeBose5.js";import{_ as f}from"./BqoOoy-a.js";import"./BSEdKPgk.js";import"./B18F2_lz.js";import"./D0ww02ZN.js";import"./CRWjC3CT.js";import"./Xs_VBmP5.js";import"./CFYL8r3V.js";import"./BC9BnLXc.js";import"./CFMQYC2y.js";import"./C3eD4HWe.js";import"./CKrGKsKZ.js";import"./CVtkxrq9.js";import"./CnlriU-7.js";import"./_dzyiV2Y.js";import"./BdoT2ima.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./DuePtXgb.js";import"./Dg6b6f8s.js";import"./DQnMOLSw.js";import"./DBZXZDU8.js";import"./BY12SjvE.js";import"./9FKpjZKd.js";import"./BOX21o1p.js";import"./CCI1_F0E.js";import"./DSIC1A7N.js";import"./Dt-H8hG_.js";import"./CeqMdjdi.js";const e=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),g={render:d=>({template:`
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
