import{i as t}from"./B2gtyV-h.js";import{g as u}from"./BVJcBgUG.js";import{V as n,g as m}from"./Bz0AvHAH.js";import{u as f}from"./CLVl6rL5.js";import{_ as l}from"./C3XOPXeD.js";import{u as g}from"./DLCnOpdB.js";import"./RQxsyxdU.js";import"./f6gYKWT5.js";import"./C-ucudUc.js";import"./53SD24Bo.js";import"./B2IxrC02.js";import"./DvUUAc5c.js";import"./BbcJJQG6.js";import"./BnJv8bNI.js";import"./okj3qyDJ.js";import"./B7ZxQ_gM.js";import"./CGdESDy3.js";import"./C4QhmNcb.js";import"./BALwooav.js";import"./CxzE6WfI.js";import"./BsOxdBIg.js";import"./DhTbjJlp.js";import"./DVK973mh.js";import"./CS5TX658.js";import"./B6C3U6x3.js";import"./ByZ6H8Q9.js";import"./oAL5f6fw.js";import"./Cai0IfA4.js";import"./zrJmgcCO.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
