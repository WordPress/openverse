import{_ as t}from"./C_KzvzgK.js";import{V as n}from"./DOsPUomk.js";import{h as s}from"./D21kBugn.js";import"./K-1Rbgrz.js";import"./CFMQYC2y.js";import"./JYtQN4fY.js";import"./DzUJZ0J9.js";import"./DEweiwTv.js";import"./DlAUqK2U.js";import"./4sVlZB-J.js";import"./C66CHCZN.js";const y={title:"Components/VLogoLoader",component:n,argTypes:{status:{default:"idle",options:["loading","idle"],control:{type:"radio"}}}},r={render:e=>({components:{VLogoLoader:n},setup(){return()=>s(n,e)}}),name:"Idle",args:{status:"idle"}},o={render:e=>({components:{VLogoLoader:n},setup(){return()=>s(n,e)}}),name:"Loading",args:{status:"loading",loadingLabel:"Loading images"}},a={render:e=>({components:{VLink:t,VLogoLoader:n},setup(){return()=>s(t,{href:"https://wordpress.org/openverse"},{default:()=>[s(n,e)]})}}),name:"Link",args:{status:"loading",loadingLabel:"Loading images"}};var d,i,p;r.parameters={...r.parameters,docs:{...(d=r.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(p=(i=r.parameters)==null?void 0:i.docs)==null?void 0:p.source}}};var g,m,L;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
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
}`,...(L=(m=o.parameters)==null?void 0:m.docs)==null?void 0:L.source}}};var c,u,l;a.parameters={...a.parameters,docs:{...(c=a.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
}`,...(l=(u=a.parameters)==null?void 0:u.docs)==null?void 0:l.source}}};const C=["Idle","Loading","Link"];export{r as Idle,a as Link,o as Loading,C as __namedExportsOrder,y as default};
