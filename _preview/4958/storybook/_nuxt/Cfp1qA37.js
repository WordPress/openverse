import{N as h,E as T,a as N}from"./CTON8dBl.js";import{_ as a}from"./DI37Eb2l.js";import{h as l}from"./lKNUlTH_.js";import"./DPAaeLdr.js";import"../sb-preview/runtime.js";const K={title:"Components/VErrorSection",component:a},o={render:E=>({components:{VErrorSection:a},setup(){return()=>l(a,E)}})},e={...o,name:"No result",args:{fetchingError:{code:h,requestKind:"search",searchType:"image",details:{searchTerm:"sad person"}}}},r={...o,name:"Server timeout",args:{fetchingError:{code:T,requestKind:"search",searchType:"image"}}},n={...o,name:"Unknown error",args:{fetchingError:{code:N,requestKind:"search",searchType:"image"}}};var s,t,c;e.parameters={...e.parameters,docs:{...(s=e.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(c=(t=e.parameters)==null?void 0:t.docs)==null?void 0:c.source}}};var m,i,p;r.parameters={...r.parameters,docs:{...(m=r.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...ErrorPageTemplate,
  name: "Server timeout",
  args: {
    fetchingError: {
      code: ECONNABORTED,
      requestKind: "search",
      searchType: "image"
    }
  }
}`,...(p=(i=r.parameters)==null?void 0:i.docs)==null?void 0:p.source}}};var d,u,g;n.parameters={...n.parameters,docs:{...(d=n.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...ErrorPageTemplate,
  name: "Unknown error",
  args: {
    fetchingError: {
      code: ERR_UNKNOWN,
      requestKind: "search",
      searchType: "image"
    }
  }
}`,...(g=(u=n.parameters)==null?void 0:u.docs)==null?void 0:g.source}}};const U=["NoResult","ServerTimeout","UnknownError"];export{e as NoResult,r as ServerTimeout,n as UnknownError,U as __namedExportsOrder,K as default};
