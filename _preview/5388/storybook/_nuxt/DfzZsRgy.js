import{i as t}from"./j3Q-zP34.js";import{g as u}from"./C-hMaVy5.js";import{V as n,g as m}from"./xBbHIPC0.js";import{u as f}from"./COoUbZHr.js";import{_ as l}from"./DLPwSW20.js";import{u as g}from"./B9Cuo1Ro.js";import"./DgrDIC-J.js";import"./DR8_TFMJ.js";import"./DECrRio6.js";import"./53SD24Bo.js";import"./DByKg8Rq.js";import"./xUhahl4a.js";import"./ClJfFvea.js";import"./DCzCyFcy.js";import"./okj3qyDJ.js";import"./Bm3FqArX.js";import"./BKOhH9JE.js";import"./CJ-njDxe.js";import"./DhLxMFu1.js";import"./f-66QnrL.js";import"./DhUVMU7d.js";import"./DhTbjJlp.js";import"./DUsHYJxR.js";import"./CZhBDPgm.js";import"./C715yFha.js";import"./CKGOzHjv.js";import"./RmKinknp.js";import"./Dq1j0f_z.js";import"./BBJ4OzBf.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="03fc55bd-87e9-45de-91c6-65720b2909c5",e._sentryDebugIdIdentifier="sentry-dbid-03fc55bd-87e9-45de-91c6-65720b2909c5")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),b={render:e=>({template:`
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
