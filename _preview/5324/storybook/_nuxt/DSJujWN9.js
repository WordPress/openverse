import{i as e}from"./C1y-dB9A.js";import{g as u}from"./CUEczsrM.js";import{V as n,g as m}from"./DIixlKJT.js";import{u as f}from"./BXlC2Afm.js";import{_ as l}from"./DtAqxEqu.js";import{u as g}from"./rltOz0pP.js";import"./BQ2uyTwE.js";import"./BUcLuzj5.js";import"./DHgysDkh.js";import"./CP2tuLu8.js";import"./DLWVrS0P.js";import"./BKGw6EjD.js";import"./ueSFnAt6.js";import"./C_jCWbT6.js";import"./DzAq6MI-.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./DDGXuWLI.js";import"./C4YS0AQy.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DhTbjJlp.js";import"./dNCV0R31.js";import"./CXxamnmK.js";import"./B0H8WDcx.js";import"./CIRXjnDb.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"./DSEYgdJX.js";import"./DN7x3K2B.js";import"./cXVshVQU.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var t=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new t.Error().stack;r&&(t._sentryDebugIds=t._sentryDebugIds||{},t._sentryDebugIds[r]="1dccd39c-60af-4dbd-868b-0d46f1c81811",t._sentryDebugIdIdentifier="sentry-dbid-1dccd39c-60af-4dbd-868b-0d46f1c81811")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:t=>({template:`
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
  `,components:{VMetadata:n,VLanguageSelect:l},setup(){f().$patch({providers:{audio:[{source_name:a.source}],image:[{source_name:e.source}]},sourceNames:{audio:[a.source],image:[e.source]}});const{t:i}=g({useScope:"global"}),c=[{metadata:m(e,i,{width:e.width,height:e.height,type:e.filetype}),media:e},{metadata:m(a,i),media:a}];return{args:t,data:c}}})},W={title:"Components/VMediaInfo/VMetadata",component:n},o={...b,name:"VMetadata"};var d,s,p;o.parameters={...o.parameters,docs:{...(d=o.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(s=o.parameters)==null?void 0:s.docs)==null?void 0:p.source}}};const X=["Default"];export{o as Default,X as __namedExportsOrder,W as default};
