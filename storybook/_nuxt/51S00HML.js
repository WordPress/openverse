import{_ as o}from"./DEBDVO2M.js";import"./CDFarRZf.js";import{D as y,h as r}from"./Bf-AzR54.js";import"./1cIS4PYo.js";import"./D9JVarWf.js";import"./B06Wl6je.js";import"./s_UyrGHf.js";import"./C49ubYrZ.js";import"./BR2QLtgc.js";import"./Nz2p3Woh.js";import"./shqyu_m_.js";import"./UQnQ_SvL.js";import"./BOvEjOPJ.js";import"./DHILWyHo.js";import"./DP0Qqza0.js";import"./6POF_SQB.js";import"./nResBSny.js";import"./B78A4_tv.js";import"./C1-0vP3w.js";import"./olEHfY3b.js";import"./bYPJlIeP.js";import"./rZ73O98I.js";import"./BF6vVg7M.js";import"./DzAq6MI-.js";import"./CVxoL6nj.js";import"./DhTbjJlp.js";import"./3QBiPIGM.js";import"./A1eQbVRq.js";import"./HitohTq8.js";import"./8vSlX9Dy.js";import"./Big7CaLo.js";import"./G-2gs7Wx.js";import"./Xl6n5ahl.js";import"./CADoQZ_l.js";import"./nHVt-A68.js";import"./DGk1paF9.js";import"./DTP0RB-8.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="82c2c2db-cfa9-449e-8198-63fb41163749",e._sentryDebugIdIdentifier="sentry-dbid-82c2c2db-cfa9-449e-8198-63fb41163749")}catch{}})();const ne={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=y("Hello, World!"),p=v=>{const b=v.target;t.value=b.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,c,i;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    value: "Search query"
  }
}`,...(i=(c=a.parameters)==null?void 0:c.docs)==null?void 0:i.source}}};var l,u,d;n.parameters={...n.parameters,docs:{...(l=n.parameters)==null?void 0:l.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VSearchBar
    },
    setup() {
      const text = ref("Hello, World!");
      const updateText = (event: Event) => {
        const target = event.target as HTMLInputElement;
        text.value = target.value;
      };
      return () => h("div", [h(VSearchBar, {
        ...args
      }, {
        default: () => h("span", {
          class: "info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",
          onChange: updateText
        }, \`\${text.value.length} chars\`)
      }), text.value]);
    }
  }),
  name: "v-model"
}`,...(d=(u=n.parameters)==null?void 0:u.docs)==null?void 0:d.source}}};var f,h,g;s.parameters={...s.parameters,docs:{...(f=s.parameters)==null?void 0:f.docs,source:{originalSource:`{
  ...Template,
  name: "With placeholder",
  args: {
    placeholder: "Search query"
  }
}`,...(g=(h=s.parameters)==null?void 0:h.docs)==null?void 0:g.source}}};const se=["Default","VModel","WithPlaceholder"];export{a as Default,n as VModel,s as WithPlaceholder,se as __namedExportsOrder,ne as default};
