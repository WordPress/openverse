import{i as t}from"./Dh2K4aY0.js";import{g as u}from"./Caf7sknz.js";import{V as n,g as m}from"./DjZQiw41.js";import{u as f}from"./DZSCtjcm.js";import{_ as l}from"./Dx2Zm-_a.js";import{u as g}from"./B9Cuo1Ro.js";import"./Bk8VSEei.js";import"./BSHtV9yS.js";import"./DUD5NJ41.js";import"./53SD24Bo.js";import"./whaKyvbR.js";import"./BLjgfQlY.js";import"./D4B1y8Wp.js";import"./S07_m3Bd.js";import"./okj3qyDJ.js";import"./Cbq1TCLb.js";import"./fL1fV1YB.js";import"./C7m8LBdt.js";import"./D1l3oJXo.js";import"./CQ3yco75.js";import"./b8e1KD_n.js";import"./DhTbjJlp.js";import"./C8lB5fex.js";import"./CKwrFVsl.js";import"./C0eb6efW.js";import"./Cpzk_0_B.js";import"./Bl5m8s2n.js";import"./DLXib-Qm.js";import"./HMv5w3uE.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
