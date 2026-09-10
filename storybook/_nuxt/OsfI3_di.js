import{r as y,h as r}from"./53SD24Bo.js";import{_ as o}from"./B1moQYhQ.js";import"./_bbq3c9C.js";import"./Bm4FmDYT.js";import"./7RO02bE1.js";import"./DZZH7AoH.js";import"./Dh8GjfY7.js";import"./cfmnUtlK.js";import"./DD0JbomO.js";import"./DZOi7sP9.js";import"./DDS--uLL.js";import"./DGyM8Eie.js";import"./DVthAQU8.js";import"./B9k6C3Hw.js";import"./8DNOLO2n.js";import"./C1DVfU3S.js";import"./iProge2w.js";import"./CdxtYFZI.js";import"./Cy_NKsXi.js";import"./B_-6Taiq.js";import"./Dm0sd39P.js";import"./CUnsfT8r.js";import"./okj3qyDJ.js";import"./Cjy74nev.js";import"./DhTbjJlp.js";import"./BqQMFj8Z.js";import"./BnbCYJz1.js";import"./dvXbmdTd.js";import"./ivjvpZKc.js";import"./DjsporFN.js";import"./DlboKt2a.js";import"./Di7dAt70.js";import"./BOewZ2sR.js";import"./D2GrBf-6.js";import"./CH5-dTGy.js";import"./DZuBxUHN.js";import"./xQ8_qGND.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="29647acb-55b3-4e8c-a1f2-abbf17eb648e",e._sentryDebugIdIdentifier="sentry-dbid-29647acb-55b3-4e8c-a1f2-abbf17eb648e")}catch{}})();const ne={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=y("Hello, World!"),p=b=>{const v=b.target;t.value=v.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,c,i;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
