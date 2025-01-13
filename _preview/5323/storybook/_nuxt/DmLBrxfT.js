import{i as t}from"./CsExZrXL.js";import{g as u}from"./DXz0h8Zn.js";import{V as n,g as m}from"./Bg9VoB9I.js";import{u as f}from"./BZyg411k.js";import{_ as l}from"./DgoTRjDL.js";import{u as g}from"./D93TPuWH.js";import"./_APRZIM1.js";import"./B6xXmqkp.js";import"./--8yokH5.js";import"./DwwldUEF.js";import"./HE8VvABB.js";import"./_Zxyb4pl.js";import"./CVIvqSzo.js";import"./zgpsPOGm.js";import"./DzAq6MI-.js";import"./5Ry8iPjm.js";import"./Dy2lpsBJ.js";import"./Dv6gP7wZ.js";import"./D2_E7_fN.js";import"./erT4Ktbo.js";import"./zDkj65pD.js";import"./DhTbjJlp.js";import"./CEYAPWql.js";import"./BlLoq69p.js";import"./BS9mcOP4.js";import"./D197vL4o.js";import"./DS5pDSwp.js";import"./BAbDw2j1.js";import"./DExoS9Kr.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
