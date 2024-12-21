import{_ as o}from"./DCF0V0Et.js";import"./D6xGyQxu.js";import{D as y,h as r}from"./Bf-AzR54.js";import"./0QUgnBzB.js";import"./D9JVarWf.js";import"./B06Wl6je.js";import"./CT9Sy3M_.js";import"./BOUW-SPp.js";import"./CXqvJHsO.js";import"./BxCgZ025.js";import"./BnJZTjE_.js";import"./CkK3diBk.js";import"./CUyQTIYr.js";import"./BsG3jt0b.js";import"./CRElLIkf.js";import"./C7lp-ITr.js";import"./BZTl3SGY.js";import"./SxvBqf-I.js";import"./BvQxCwAx.js";import"./Tu1w6jvB.js";import"./DBWmBUzF.js";import"./eAGCzEdq.js";import"./G0IPDLoE.js";import"./DzAq6MI-.js";import"./CVxoL6nj.js";import"./DhTbjJlp.js";import"./CgF47Vqu.js";import"./D2OdtNy-.js";import"./DmNhhvCU.js";import"./CO4aZKIX.js";import"./p8nc5Li4.js";import"./6ItBZc85.js";import"./v8hTCxed.js";import"./D3fY7LA9.js";import"./EvZx83Uz.js";import"./C_P9rAAR.js";import"./B3qX5PDY.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="82c2c2db-cfa9-449e-8198-63fb41163749",e._sentryDebugIdIdentifier="sentry-dbid-82c2c2db-cfa9-449e-8198-63fb41163749")}catch{}})();const ne={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=y("Hello, World!"),p=v=>{const b=v.target;t.value=b.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,c,i;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
