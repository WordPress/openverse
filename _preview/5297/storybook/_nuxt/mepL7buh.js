import{N as h,E as l,a as T}from"./CUyQTIYr.js";import{_ as o}from"./WsHiQs6a.js";import"./D6xGyQxu.js";import{h as N}from"./Bf-AzR54.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8f084880-5604-4777-97ec-6814a999aec7",e._sentryDebugIdIdentifier="sentry-dbid-8f084880-5604-4777-97ec-6814a999aec7")}catch{}})();const K={title:"Components/VErrorSection",component:o},s={render:e=>({components:{VErrorSection:o},setup(){return()=>N(o,e)}})},r={...s,name:"No result",args:{fetchingError:{code:h,requestKind:"search",searchType:"image",details:{searchTerm:"sad person"}}}},n={...s,name:"Server timeout",args:{fetchingError:{code:l,requestKind:"search",searchType:"image"}}},a={...s,name:"Unknown error",args:{fetchingError:{code:T,requestKind:"search",searchType:"image"}}};var c,i,m;r.parameters={...r.parameters,docs:{...(c=r.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
}`,...(m=(i=r.parameters)==null?void 0:i.docs)==null?void 0:m.source}}};var d,p,u;n.parameters={...n.parameters,docs:{...(d=n.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(f=(E=a.parameters)==null?void 0:E.docs)==null?void 0:f.source}}};const U=["NoResult","ServerTimeout","UnknownError"];export{r as NoResult,n as ServerTimeout,a as UnknownError,U as __namedExportsOrder,K as default};
