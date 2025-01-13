import{i as t}from"./Dxoy6LB0.js";import{g as u}from"./BpaejRYu.js";import{V as n,g as m}from"./6KYwHBod.js";import{u as f}from"./KlWK2kB1.js";import{_ as l}from"./CTLJpYmk.js";import{u as g}from"./D93TPuWH.js";import"./CjQ0HQF0.js";import"./CFZbsX2Q.js";import"./CD6Nr1ia.js";import"./DwwldUEF.js";import"./BIohVJVH.js";import"./CiJxsHst.js";import"./C6VqcP4x.js";import"./DcMSHMAp.js";import"./DzAq6MI-.js";import"./B67cIdux.js";import"./Cqs9wCPQ.js";import"./D9b6d0V7.js";import"./BufT_yKp.js";import"./Bu-vEs7l.js";import"./Dwl_h6Xz.js";import"./DhTbjJlp.js";import"./BfrDyOx-.js";import"./vH24kOL-.js";import"./Ct9P1Zdp.js";import"./Bl4H7SX1.js";import"./DZZ1Fr_1.js";import"./rq0rg1X-.js";import"./BKu7KIww.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
