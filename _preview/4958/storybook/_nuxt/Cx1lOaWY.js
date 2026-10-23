import{u as c}from"./2vq21tXV.js";import{i as t}from"./vQCScaZm.js";import{g as u}from"./DdMEaL1I.js";import{V as p,g as r}from"./DvUoRkTl.js";import{u as l}from"./QKPGpISV.js";import{_ as f}from"./Be_b4sgE.js";import"./BSEdKPgk.js";import"./lKNUlTH_.js";import"./D0ww02ZN.js";import"./Xs_VBmP5.js";import"./xwskLidM.js";import"./CIg47mny.js";import"./CFMQYC2y.js";import"./CsX9763x.js";import"./BR9eDTPM.js";import"./CVtkxrq9.js";import"./DivIZ7Lb.js";import"./CA4HNXs5.js";import"./MXhTc5uu.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./C67TMzvP.js";import"./DYkE03l5.js";import"./DQnMOLSw.js";import"./5ehHOY6F.js";import"./9Q23NzEb.js";import"./C0voMBC3.js";import"./BOX21o1p.js";import"./CeIx8O89.js";import"./CzMkt2mC.js";import"./Dt-H8hG_.js";import"./CSjnkXPe.js";const e=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),g={render:d=>({template:`
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
  `,components:{VMetadata:p,VLanguageSelect:f},setup(){l().$patch({providers:{audio:[{source_name:e.source}],image:[{source_name:t.source}]},sourceNames:{audio:[e.source],image:[t.source]}});const o=c({useScope:"global"}),n=[{metadata:r(t,o,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:r(e,o),media:e}];return{args:d,data:n}}})},U={title:"Components/VMediaInfo/VMetadata",component:p},a={...g,name:"VMetadata"};var i,m,s;a.parameters={...a.parameters,docs:{...(i=a.parameters)==null?void 0:i.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(s=(m=a.parameters)==null?void 0:m.docs)==null?void 0:s.source}}};const W=["Default"];export{a as Default,W as __namedExportsOrder,U as default};
