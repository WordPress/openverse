import{h as s}from"./53SD24Bo.js";import{_ as d}from"./B7ZxQ_gM.js";import{V as n}from"./BLxR6Tk0.js";import"./RQxsyxdU.js";import"./CGdESDy3.js";import"./C4QhmNcb.js";import"./BALwooav.js";import"./CxzE6WfI.js";import"./BsOxdBIg.js";import"./DhTbjJlp.js";import"./hEiMHrFo.js";import"./7RO02bE1.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8cbca763-e99b-48b8-8107-e224f6ef7f46",e._sentryDebugIdIdentifier="sentry-dbid-8cbca763-e99b-48b8-8107-e224f6ef7f46")}catch{}})();const O={title:"Components/VLogoLoader",component:n,argTypes:{status:{default:"idle",options:["loading","idle"],control:{type:"radio"}}}},r={render:e=>({components:{VLogoLoader:n},setup(){return()=>s(n,e)}}),name:"Idle",args:{status:"idle"}},o={render:e=>({components:{VLogoLoader:n},setup(){return()=>s(n,e)}}),name:"Loading",args:{status:"loading",loadingLabel:"Loading images"}},a={render:e=>({components:{VLink:d,VLogoLoader:n},setup(){return()=>s(d,{href:"https://wordpress.org/openverse"},{default:()=>[s(n,e)]})}}),name:"Link",args:{status:"loading",loadingLabel:"Loading images"}};var i,g,p;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VLogoLoader
    },
    setup() {
      return () => h(VLogoLoader, args);
    }
  }),
  name: "Idle",
  args: {
    status: "idle"
  }
}`,...(p=(g=r.parameters)==null?void 0:g.docs)==null?void 0:p.source}}};var m,c,u;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VLogoLoader
    },
    setup() {
      return () => h(VLogoLoader, args);
    }
  }),
  name: "Loading",
  args: {
    status: "loading",
    loadingLabel: "Loading images"
  }
}`,...(u=(c=o.parameters)==null?void 0:c.docs)==null?void 0:u.source}}};var l,L,f;a.parameters={...a.parameters,docs:{...(l=a.parameters)==null?void 0:l.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VLink,
      VLogoLoader
    },
    setup() {
      return () => h(VLink, {
        href: "https://wordpress.org/openverse"
      }, {
        default: () => [h(VLogoLoader, args)]
      });
    }
  }),
  name: "Link",
  args: {
    status: "loading",
    loadingLabel: "Loading images"
  }
}`,...(f=(L=a.parameters)==null?void 0:L.docs)==null?void 0:f.source}}};const T=["Idle","Loading","Link"];export{r as Idle,a as Link,o as Loading,T as __namedExportsOrder,O as default};
