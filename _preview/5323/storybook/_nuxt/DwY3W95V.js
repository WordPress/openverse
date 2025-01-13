import{r as b,h as r}from"./DwwldUEF.js";import{_ as o}from"./BulC_GwV.js";import"./_APRZIM1.js";import"./B7XE-qnX.js";import"./Ck0CgHQL.js";import"./C2YIn4kX.js";import"./DjaEaIMA.js";import"./DjYgPbDk.js";import"./BNZBDzqs.js";import"./CVIvqSzo.js";import"./B6xXmqkp.js";import"./hEU2uDsT.js";import"./DbbxtPJM.js";import"./BAbDw2j1.js";import"./Chgn5vcY.js";import"./DfKQSGJ_.js";import"./HE8VvABB.js";import"./BZyg411k.js";import"./--8yokH5.js";import"./D2_E7_fN.js";import"./BcTEa7d-.js";import"./zgpsPOGm.js";import"./DzAq6MI-.js";import"./DKrssSK2.js";import"./DhTbjJlp.js";import"./BBTP8zYm.js";import"./CZGWR9g8.js";import"./erT4Ktbo.js";import"./zDkj65pD.js";import"./Dv6gP7wZ.js";import"./D197vL4o.js";import"./DS5pDSwp.js";import"./5Ry8iPjm.js";import"./Dy2lpsBJ.js";import"./B63HZfbS.js";import"./BS9mcOP4.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="9fcd1252-293d-4b04-9199-aed4e79329c8",e._sentryDebugIdIdentifier="sentry-dbid-9fcd1252-293d-4b04-9199-aed4e79329c8")}catch{}})();const ae={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=b("Hello, World!"),p=v=>{const y=v.target;t.value=y.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,c,i;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
