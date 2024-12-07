import{i as t}from"./vQCScaZm.js";import{g as c}from"./D1zI34GW.js";import{V as s,g as r}from"./QcP8i8h4.js";import{u}from"./gmSLTnsl.js";import{_ as l}from"./BQyX743E.js";import{u as f}from"./DyBDyB1K.js";import"./CRWjC3CT.js";import"./D0ww02ZN.js";import"./Xs_VBmP5.js";import"./Cpw-XNzg.js";import"./KtaE-n0E.js";import"./D21kBugn.js";import"./CszWEYKx.js";import"./CVtkxrq9.js";import"./C_KzvzgK.js";import"./K-1Rbgrz.js";import"./CFMQYC2y.js";import"./JYtQN4fY.js";import"./DzUJZ0J9.js";import"./DEweiwTv.js";import"./DlAUqK2U.js";import"./BMFse2nb.js";import"./DQnMOLSw.js";import"./DBH8h2qE.js";import"./Cs0FBLOW.js";import"./CWkdu0ct.js";import"./BOX21o1p.js";import"./DmWT6tLV.js";import"./Dt-H8hG_.js";import"./BQsRc94L.js";import"./C66CHCZN.js";import"./DSfKr7W2.js";import"./C1YDwe8s.js";const e=c({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),g={render:d=>({template:`
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
  `,components:{VMetadata:s,VLanguageSelect:l},setup(){u().$patch({providers:{audio:[{source_name:e.source}],image:[{source_name:t.source}]},sourceNames:{audio:[e.source],image:[t.source]}});const{t:o}=f({useScope:"global"}),n=[{metadata:r(t,o,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:r(e,o),media:e}];return{args:d,data:n}}})},W={title:"Components/VMediaInfo/VMetadata",component:s},a={...g,name:"VMetadata"};var i,m,p;a.parameters={...a.parameters,docs:{...(i=a.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(m=a.parameters)==null?void 0:m.docs)==null?void 0:p.source}}};const X=["Default"];export{a as Default,X as __namedExportsOrder,W as default};
