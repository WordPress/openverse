import{_ as o}from"./C9RX2jFx.js";import"./BQ2uyTwE.js";import{I as b,h as r}from"./ueSFnAt6.js";import"./kW-dWg3h.js";import"./dNCV0R31.js";import"./cS2ccka-.js";import"./CIbAl0As.js";import"./BOH1sSDC.js";import"./De9CcUDw.js";import"./BKvBQNfv.js";import"./BKGw6EjD.js";import"./BUcLuzj5.js";import"./D9PGBJDx.js";import"./CxIz9G_3.js";import"./DSEYgdJX.js";import"./EYmIadoG.js";import"./nu0uObuU.js";import"./CP2tuLu8.js";import"./BXlC2Afm.js";import"./DHgysDkh.js";import"./C4YS0AQy.js";import"./5wCrcqN-.js";import"./C_jCWbT6.js";import"./DzAq6MI-.js";import"./NuBHaYAk.js";import"./DhTbjJlp.js";import"./BYeRT9qC.js";import"./D2P1fKwO.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DDGXuWLI.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./DnxirkMG.js";import"./CIRXjnDb.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="8342f498-c06f-461e-8435-67537db72339",e._sentryDebugIdIdentifier="sentry-dbid-8342f498-c06f-461e-8435-67537db72339")}catch{}})();const ne={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=b("Hello, World!"),p=v=>{const y=v.target;t.value=y.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,i,c;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    value: "Search query"
  }
}`,...(c=(i=a.parameters)==null?void 0:i.docs)==null?void 0:c.source}}};var l,u,d;n.parameters={...n.parameters,docs:{...(l=n.parameters)==null?void 0:l.docs,source:{originalSource:`{
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
