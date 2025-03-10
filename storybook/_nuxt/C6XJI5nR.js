import{h}from"./53SD24Bo.js";import{N as l,E as T,a as N}from"./BW6nfHgy.js";import{_ as o}from"./HitB0DaN.js";import"./RQxsyxdU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="040506ff-9500-4b43-94ce-88522da3fa52",e._sentryDebugIdIdentifier="sentry-dbid-040506ff-9500-4b43-94ce-88522da3fa52")}catch{}})();const O={title:"Components/VErrorSection",component:o},s={render:e=>({components:{VErrorSection:o},setup(){return()=>h(o,e)}})},r={...s,name:"No result",args:{fetchingError:{code:l,requestKind:"search",searchType:"image",details:{searchTerm:"sad person"}}}},n={...s,name:"Server timeout",args:{fetchingError:{code:T,requestKind:"search",searchType:"image"}}},a={...s,name:"Unknown error",args:{fetchingError:{code:N,requestKind:"search",searchType:"image"}}};var c,i,m;r.parameters={...r.parameters,docs:{...(c=r.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
}`,...(u=(p=n.parameters)==null?void 0:p.docs)==null?void 0:u.source}}};var g,f,E;a.parameters={...a.parameters,docs:{...(g=a.parameters)==null?void 0:g.docs,source:{originalSource:`{
  ...ErrorPageTemplate,
  name: "Unknown error",
  args: {
    fetchingError: {
      code: ERR_UNKNOWN,
      requestKind: "search",
      searchType: "image"
    }
  }
}`,...(E=(f=a.parameters)==null?void 0:f.docs)==null?void 0:E.source}}};const K=["NoResult","ServerTimeout","UnknownError"];export{r as NoResult,n as ServerTimeout,a as UnknownError,K as __namedExportsOrder,O as default};
