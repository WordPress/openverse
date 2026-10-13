import{h as r,r as b}from"./DmrXErv4.js";import{_ as o}from"./C-LiyW8d.js";import"./Ceavzuo-.js";import"./BLPCtnQ2.js";import"./BxtqxG2r.js";import"./DqDG9Ezv.js";import"./CVvkZ7Vc.js";import"./DHjch8ts.js";import"./-2B6Z20n.js";import"./Dbo3V4Mp.js";import"./9mLNX8sN.js";import"./DNv5NVgs.js";import"./i2yG8VlY.js";import"./Dp2jPxn_.js";import"./Bp0tQXh7.js";import"./COQlapGP.js";import"./JU2JEH3o.js";import"./Dyqkukzd.js";import"./DoeNFUMW.js";import"./BS_ZT77X.js";import"./FWiT1Y5Q.js";import"./C_FySRQg.js";import"./DzAq6MI-.js";import"./DQVrT9A6.js";import"./DhTbjJlp.js";import"./C3B2fpuk.js";import"./QAUZVczv.js";import"./CdX5GYQk.js";import"./qy-jYTsH.js";import"./BayljJpb.js";import"./0xbGHjBU.js";import"./lCCmDL6e.js";import"./CtkidDXQ.js";import"./CMZS2cOm.js";import"./Ck0gvfbg.js";import"./5TRjGj2w.js";import"./us_YXsMU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="5646ed70-a02f-4688-9882-a22834113ce5",e._sentryDebugIdIdentifier="sentry-dbid-5646ed70-a02f-4688-9882-a22834113ce5")}catch{}})();const ne={title:"Components/VHeader/Search bar",component:o,argTypes:{onSubmit:{action:"submit"}}},x={render:e=>({components:{VSearchBar:o},setup(){return()=>r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},a={...x,name:"Default",args:{value:"Search query"}},n={render:e=>({components:{VSearchBar:o},setup(){const t=b("Hello, World!"),p=v=>{const y=v.target;t.value=y.value};return()=>r("div",[r(o,{...e},{default:()=>r("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:p},`${t.value.length} chars`)}),t.value])}}),name:"v-model"},s={...x,name:"With placeholder",args:{placeholder:"Search query"}};var m,i,c;a.parameters={...a.parameters,docs:{...(m=a.parameters)==null?void 0:m.docs,source:{originalSource:`{
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
