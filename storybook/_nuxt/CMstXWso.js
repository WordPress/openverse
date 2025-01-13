import{r as b,h as r}from"./DwwldUEF.js";import{_ as o}from"./Bc-WYXpa.js";import"./BKd6qjwJ.js";import"./CFuKNNjc.js";import"./Ck0CgHQL.js";import"./BcaGrvtg.js";import"./6lK7d3wu.js";import"./CGWvVp-6.js";import"./DyntKXIc.js";import"./B_JavP0r.js";import"./DyjmqLvs.js";import"./TJSYFxys.js";import"./DXt3Hw-9.js";import"./DrQM85Nc.js";import"./DeIUwsAH.js";import"./Bc_6hboB.js";import"./BJKkpTjt.js";import"./DIa_evZO.js";import"./D5nIdk7e.js";import"./DEzOOYTC.js";import"./BA2RD0IG.js";import"./BwtrEtqR.js";import"./DzAq6MI-.js";import"./DKrssSK2.js";import"./DhTbjJlp.js";import"./Bm4Amnim.js";import"./BYD-UmPb.js";import"./D318SDY2.js";import"./BMyQprRt.js";import"./DjJGxhuO.js";import"./R_--_Flr.js";import"./Duzn9Bak.js";import"./B7G-YaxP.js";import"./Efi66Qad.js";import"./DV0jNGwa.js";import"./DJYCrh4A.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="9fcd1252-293d-4b04-9199-aed4e79329c8",e._sentryDebugIdIdentifier="sentry-dbid-9fcd1252-293d-4b04-9199-aed4e79329c8")}catch{}})();const ae={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=b("Hello, World!"),p=v=>{const y=v.target;t.value=y.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,c,i;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    value: "Search query"
  }
}`,...(i=(c=a.parameters)==null?void 0:c.docs)==null?void 0:i.source}}};var d,l,u;n.parameters={...n.parameters,docs:{...(d=n.parameters)==null?void 0:d.docs,source:{originalSource:`{
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
}`,...(u=(l=n.parameters)==null?void 0:l.docs)==null?void 0:u.source}}};var f,h,g;s.parameters={...s.parameters,docs:{...(f=s.parameters)==null?void 0:f.docs,source:{originalSource:`{
  ...Template,
  name: "With placeholder",
  args: {
    placeholder: "Search query"
  }
}`,...(g=(h=s.parameters)==null?void 0:h.docs)==null?void 0:g.source}}};const ne=["Default","VModel","WithPlaceholder"];export{a as Default,n as VModel,s as WithPlaceholder,ne as __namedExportsOrder,ae as default};
