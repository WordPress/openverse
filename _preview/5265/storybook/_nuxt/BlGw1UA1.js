import{r as b,h as r}from"./DwwldUEF.js";import{_ as o}from"./IVjSO0Zc.js";import"./CjQ0HQF0.js";import"./li7pUmcm.js";import"./Ck0CgHQL.js";import"./B8C4Bbpu.js";import"./8aqEA3wi.js";import"./B7XfVgP-.js";import"./Gc5ScyLZ.js";import"./C6VqcP4x.js";import"./CFZbsX2Q.js";import"./Ley1esUq.js";import"./C0pA7UPR.js";import"./rq0rg1X-.js";import"./CUsfujdM.js";import"./DmsD6orq.js";import"./BIohVJVH.js";import"./KlWK2kB1.js";import"./CD6Nr1ia.js";import"./BufT_yKp.js";import"./BuC5_mLh.js";import"./DcMSHMAp.js";import"./DzAq6MI-.js";import"./DKrssSK2.js";import"./DhTbjJlp.js";import"./DBfUdbPz.js";import"./CTGRm2NM.js";import"./Bu-vEs7l.js";import"./Dwl_h6Xz.js";import"./D9b6d0V7.js";import"./Bl4H7SX1.js";import"./DZZ1Fr_1.js";import"./B67cIdux.js";import"./Cqs9wCPQ.js";import"./Cx5uXtjF.js";import"./Ct9P1Zdp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="9fcd1252-293d-4b04-9199-aed4e79329c8",e._sentryDebugIdIdentifier="sentry-dbid-9fcd1252-293d-4b04-9199-aed4e79329c8")}catch{}})();const ae={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=b("Hello, World!"),p=v=>{const y=v.target;t.value=y.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,c,i;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
