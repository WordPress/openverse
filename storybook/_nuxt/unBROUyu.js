import{h}from"./DmrXErv4.js";import{N as l,E as T,a as N}from"./DNv5NVgs.js";import{_ as o}from"./Dac3IqEL.js";import"./Ceavzuo-.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="76f68dea-727c-4bee-a245-4bd28a9a3054",e._sentryDebugIdIdentifier="sentry-dbid-76f68dea-727c-4bee-a245-4bd28a9a3054")}catch{}})();const O={title:"Components/VErrorSection",component:o},s={render:e=>({components:{VErrorSection:o},setup(){return()=>h(o,e)}})},r={...s,name:"No result",args:{fetchingError:{code:l,requestKind:"search",searchType:"image",details:{searchTerm:"sad person"}}}},n={...s,name:"Server timeout",args:{fetchingError:{code:T,requestKind:"search",searchType:"image"}}},a={...s,name:"Unknown error",args:{fetchingError:{code:N,requestKind:"search",searchType:"image"}}};var c,d,i;r.parameters={...r.parameters,docs:{...(c=r.parameters)==null?void 0:c.docs,source:{originalSource:`{
  ...ErrorPageTemplate,
  name: "No result",
  args: {
    fetchingError: {
      code: NO_RESULT,
      requestKind: "search",
      searchType: "image",
      details: {
        searchTerm: "sad person"
      }
    }
  }
}`,...(i=(d=r.parameters)==null?void 0:d.docs)==null?void 0:i.source}}};var m,p,u;n.parameters={...n.parameters,docs:{...(m=n.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...ErrorPageTemplate,
  name: "Server timeout",
  args: {
    fetchingError: {
      code: ECONNABORTED,
      requestKind: "search",
      searchType: "image"
    }
  }
}`,...(u=(p=n.parameters)==null?void 0:p.docs)==null?void 0:u.source}}};var g,E,f;a.parameters={...a.parameters,docs:{...(g=a.parameters)==null?void 0:g.docs,source:{originalSource:`{
  ...ErrorPageTemplate,
  name: "Unknown error",
  args: {
    fetchingError: {
      code: ERR_UNKNOWN,
      requestKind: "search",
      searchType: "image"
    }
  }
}`,...(f=(E=a.parameters)==null?void 0:E.docs)==null?void 0:f.source}}};const K=["NoResult","ServerTimeout","UnknownError"];export{r as NoResult,n as ServerTimeout,a as UnknownError,K as __namedExportsOrder,O as default};
