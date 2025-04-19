import{i as t}from"./DV-MSd9o.js";import{g as u}from"./CjDOQofX.js";import{V as n,g as m}from"./BREDd4xz.js";import{u as f}from"./CnJShkNX.js";import{_ as l}from"./BJCm43Of.js";import{u as g}from"./B9Cuo1Ro.js";import"./DxXQfK2h.js";import"./CGl8BGyI.js";import"./Ca-grqql.js";import"./53SD24Bo.js";import"./JKyArXdZ.js";import"./BB93wJtT.js";import"./DEUQKZ_9.js";import"./DCBI9Hp4.js";import"./okj3qyDJ.js";import"./COHSvtot.js";import"./CbQ_U0bA.js";import"./1q_AdtTO.js";import"./GK6z1vC-.js";import"./CO_nLv6a.js";import"./DY7Jae7t.js";import"./DhTbjJlp.js";import"./CjdvG5-R.js";import"./DFG8o1G5.js";import"./m1m5Z0c3.js";import"./Do357AjE.js";import"./Ab-gfhxw.js";import"./BfmvDfJj.js";import"./_3a1JHAB.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
  `,components:{VMetadata:n,VLanguageSelect:l},setup(){f().$patch({providers:{audio:[{source_name:a.source}],image:[{source_name:t.source}]},sourceNames:{audio:[a.source],image:[t.source]}});const{t:i}=g({useScope:"global"}),c=[{metadata:m(t,i,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:m(a,i),media:a}];return{args:e,data:c}}})},U={title:"Components/VMediaInfo/VMetadata",component:n},o={...b,name:"VMetadata"};var s,d,p;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(d=o.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};const W=["Default"];export{o as Default,W as __namedExportsOrder,U as default};
