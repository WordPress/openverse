import{N as h,E as l,a as T}from"./D9PGBJDx.js";import{_ as s}from"./RgqnWT3a.js";import"./BQ2uyTwE.js";import{h as N}from"./ueSFnAt6.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="77fc85ef-947e-4dad-82f7-9c82d6784d1f",e._sentryDebugIdIdentifier="sentry-dbid-77fc85ef-947e-4dad-82f7-9c82d6784d1f")}catch{}})();const K={title:"Components/VErrorSection",component:s},a={render:e=>({components:{VErrorSection:s},setup(){return()=>N(s,e)}})},r={...a,name:"No result",args:{fetchingError:{code:h,requestKind:"search",searchType:"image",details:{searchTerm:"sad person"}}}},n={...a,name:"Server timeout",args:{fetchingError:{code:l,requestKind:"search",searchType:"image"}}},o={...a,name:"Unknown error",args:{fetchingError:{code:T,requestKind:"search",searchType:"image"}}};var c,d,i;r.parameters={...r.parameters,docs:{...(c=r.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
}`,...(u=(p=n.parameters)==null?void 0:p.docs)==null?void 0:u.source}}};var g,f,E;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
  ...ErrorPageTemplate,
  name: "Unknown error",
  args: {
    fetchingError: {
      code: ERR_UNKNOWN,
      requestKind: "search",
      searchType: "image"
    }
  }
}`,...(E=(f=o.parameters)==null?void 0:f.docs)==null?void 0:E.source}}};const U=["NoResult","ServerTimeout","UnknownError"];export{r as NoResult,n as ServerTimeout,o as UnknownError,U as __namedExportsOrder,K as default};
