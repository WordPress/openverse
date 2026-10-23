import{h as r,r as b}from"./DmrXErv4.js";import{_ as o}from"./D5PjIuqX.js";import"./Cre_5D1H.js";import"./CwanrMv1.js";import"./BxtqxG2r.js";import"./b7jhXYyt.js";import"./CDE4LuQ1.js";import"./CoJdQgQ3.js";import"./Boj1x2qa.js";import"./P7ZX4TMp.js";import"./BWJ9rAf_.js";import"./D8RLh9Dr.js";import"./DFZUF_34.js";import"./B3KNKrKa.js";import"./D7WD_DXd.js";import"./D_KYnWat.js";import"./wMBvb-CP.js";import"./CdQaOBNt.js";import"./C7sHCGoX.js";import"./B_dsH32H.js";import"./CEG4L8Wc.js";import"./CT8Zrxvs.js";import"./DzAq6MI-.js";import"./DQVrT9A6.js";import"./DhTbjJlp.js";import"./rvIuDPez.js";import"./7Q2jAAAV.js";import"./rMKLwKwR.js";import"./Dv0Nl23j.js";import"./Bn7RUpRV.js";import"./BRHrr7ck.js";import"./Bpr67t9y.js";import"./DWRfakdt.js";import"./CCN4kZnP.js";import"./OMXwMIS8.js";import"./Dt13xSQI.js";import"./zcyFsLMi.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="5646ed70-a02f-4688-9882-a22834113ce5",e._sentryDebugIdIdentifier="sentry-dbid-5646ed70-a02f-4688-9882-a22834113ce5")}catch{}})();const ne={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=b("Hello, World!"),p=v=>{const y=v.target;t.value=y.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,i,c;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
