import{_ as d}from"./A1b6Lb8y.js";import{V as n}from"./Bn9Fr5ZW.js";import"./BQ2uyTwE.js";import{h as s}from"./ueSFnAt6.js";import"./BQNGXNMh.js";import"./DDGXuWLI.js";import"./C4YS0AQy.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DhTbjJlp.js";import"./DNYxwfpN.js";import"./cS2ccka-.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="3bf7377a-dd67-4dd1-ac9c-d8cf9f8cb3a0",e._sentryDebugIdIdentifier="sentry-dbid-3bf7377a-dd67-4dd1-ac9c-d8cf9f8cb3a0")}catch{}})();const O={title:"Components/VLogoLoader",component:n,argTypes:{status:{default:"idle",options:["loading","idle"],control:{type:"radio"}}}},r={render:e=>({components:{VLogoLoader:n},setup(){return()=>s(n,e)}}),name:"Idle",args:{status:"idle"}},o={render:e=>({components:{VLogoLoader:n},setup(){return()=>s(n,e)}}),name:"Loading",args:{status:"loading",loadingLabel:"Loading images"}},a={render:e=>({components:{VLink:d,VLogoLoader:n},setup(){return()=>s(d,{href:"https://wordpress.org/openverse"},{default:()=>[s(n,e)]})}}),name:"Link",args:{status:"loading",loadingLabel:"Loading images"}};var i,g,p;r.parameters={...r.parameters,docs:{...(i=r.parameters)==null?void 0:i.docs,source:{originalSource:`{
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
