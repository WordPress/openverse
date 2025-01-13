import{i as t}from"./D6fHbuVq.js";import{g as u}from"./BAVS4-WL.js";import{V as n,g as m}from"./Bl3CL7bH.js";import{u as f}from"./DIa_evZO.js";import{_ as l}from"./BALfVpiu.js";import{u as g}from"./D93TPuWH.js";import"./BKd6qjwJ.js";import"./DyjmqLvs.js";import"./D5nIdk7e.js";import"./DwwldUEF.js";import"./BJKkpTjt.js";import"./DMO26O-W.js";import"./B_JavP0r.js";import"./BwtrEtqR.js";import"./DzAq6MI-.js";import"./B7G-YaxP.js";import"./Efi66Qad.js";import"./DjJGxhuO.js";import"./DEzOOYTC.js";import"./D318SDY2.js";import"./BMyQprRt.js";import"./DhTbjJlp.js";import"./AjqA5eiB.js";import"./C09Gv4cW.js";import"./DJYCrh4A.js";import"./R_--_Flr.js";import"./Duzn9Bak.js";import"./DrQM85Nc.js";import"./DXYZpz7U.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
