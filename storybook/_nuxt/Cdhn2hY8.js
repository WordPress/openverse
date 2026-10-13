import{i as t}from"./BeEBBIT-.js";import{g as u}from"./Dr5jr8fN.js";import{V as n,g as m}from"./B68A8Yvf.js";import{u as f}from"./Dyqkukzd.js";import{_ as l}from"./BxMOzCVO.js";import{u as g}from"./D5Za6x0E.js";import"./Ceavzuo-.js";import"./9mLNX8sN.js";import"./DoeNFUMW.js";import"./DmrXErv4.js";import"./JU2JEH3o.js";import"./CS1FkDVx.js";import"./Dbo3V4Mp.js";import"./C_FySRQg.js";import"./DzAq6MI-.js";import"./CtkidDXQ.js";import"./CMZS2cOm.js";import"./BayljJpb.js";import"./BS_ZT77X.js";import"./Ck0gvfbg.js";import"./CdX5GYQk.js";import"./qy-jYTsH.js";import"./DhTbjJlp.js";import"./C4vooYs6.js";import"./DIkXdRcj.js";import"./us_YXsMU.js";import"./0xbGHjBU.js";import"./lCCmDL6e.js";import"./Dp2jPxn_.js";import"./DhgREJNi.js";import"./Dx-3nI8A.js";import"./CJ7FTku9.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="518c23a7-6712-40e6-bf1d-4475ef041dfd",e._sentryDebugIdIdentifier="sentry-dbid-518c23a7-6712-40e6-bf1d-4475ef041dfd")}catch{}})();const a=u({originalTitle:"Test Audio",sensitivity:[],isSensitive:!1}),y={render:e=>({template:`
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
  `,components:{VMetadata:n,VLanguageSelect:l},setup(){f().$patch({providers:{audio:[{source_name:a.source}],image:[{source_name:t.source}]},sourceNames:{audio:[a.source],image:[t.source]}});const{t:i}=g({useScope:"global"}),c=[{metadata:m(t,i,{width:t.width,height:t.height,type:t.filetype}),media:t},{metadata:m(a,i),media:a}];return{args:e,data:c}}})},W={title:"Components/VMediaInfo/VMetadata",component:n},o={...y,name:"VMetadata"};var s,d,p;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
  ...Template,
  name: "VMetadata"
}`,...(p=(d=o.parameters)==null?void 0:d.docs)==null?void 0:p.source}}};const X=["Default"];export{o as Default,X as __namedExportsOrder,W as default};
