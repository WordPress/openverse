import{r as b,h as r}from"./53SD24Bo.js";import{_ as o}from"./lrfn3u1q.js";import"./Bk8VSEei.js";import"./D9o9W2R6.js";import"./7RO02bE1.js";import"./D1nsP1gg.js";import"./BoVjc2lE.js";import"./9SSb1GlH.js";import"./CI6-PtcM.js";import"./D4B1y8Wp.js";import"./BSHtV9yS.js";import"./DBpyOWk7.js";import"./Cx3b_-up.js";import"./DLXib-Qm.js";import"./7RAMVlBS.js";import"./CA_M5S-4.js";import"./whaKyvbR.js";import"./DZSCtjcm.js";import"./DUD5NJ41.js";import"./D1l3oJXo.js";import"./B8akBo1x.js";import"./S07_m3Bd.js";import"./okj3qyDJ.js";import"./Cjy74nev.js";import"./DhTbjJlp.js";import"./yS2SWVnn.js";import"./8cLBg1iv.js";import"./CQ3yco75.js";import"./b8e1KD_n.js";import"./C7m8LBdt.js";import"./Cpzk_0_B.js";import"./Bl5m8s2n.js";import"./Cbq1TCLb.js";import"./fL1fV1YB.js";import"./DqnqsLzS.js";import"./C0eb6efW.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="9fcd1252-293d-4b04-9199-aed4e79329c8",e._sentryDebugIdIdentifier="sentry-dbid-9fcd1252-293d-4b04-9199-aed4e79329c8")}catch{}})();const ae={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=b("Hello, World!"),p=v=>{const y=v.target;t.value=y.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,c,i;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
