import{_ as t}from"./CoRMBWob.js";import{G as y,h as e}from"./lKNUlTH_.js";import"./CSy7Uc4e.js";import"./C67TMzvP.js";import"./CzMkt2mC.js";import"./D218PAw5.js";import"./RevM6cLn.js";import"./nLTbcOiO.js";import"./xwskLidM.js";import"./DivIZ7Lb.js";import"./C0voMBC3.js";import"./CFMQYC2y.js";import"./Dt-H8hG_.js";import"./CTON8dBl.js";import"./QKPGpISV.js";import"./D0ww02ZN.js";import"./CeIx8O89.js";import"./BR9eDTPM.js";import"./CVtkxrq9.js";import"./Xs_VBmP5.js";import"./Cpj98o6Y.js";import"./Ci7G4jyV.js";import"./DC-AD4tD.js";import"./C9bMQDiX.js";import"./DlAUqK2U.js";import"./DAtDKoKx.js";import"./bBgZBGC4.js";import"./MXhTc5uu.js";import"./CuPsdpTl.js";import"./9Q23NzEb.js";import"./BOX21o1p.js";import"./CA4HNXs5.js";import"./CIg47mny.js";import"./DLmQARLo.js";import"./5ehHOY6F.js";const re={title:"Components/VHeader/Search bar",component:t,argTypes:{onSubmit:{action:"submit"}}},x={render:n=>({components:{VSearchBar:t},setup(){return()=>e(t,{...n},{default:()=>e("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default"},"12,345 results")})}})},r={...x,name:"Default",args:{value:"Search query"}},o={render:n=>({components:{VSearchBar:t},setup(){const s=y("Hello, World!"),g=v=>{const S=v.target;s.value=S.value};return()=>e("div",[e(t,{...n},{default:()=>e("span",{class:"info-8 text-xs font-semibold text-secondary mx-4 whitespace-nowrap group-hover:text-default group-focus:text-default",onChange:g},`${s.value.length} chars`)}),s.value])}}),name:"v-model"},a={...x,name:"With placeholder",args:{placeholder:"Search query"}};var p,m,c;r.parameters={...r.parameters,docs:{...(p=r.parameters)==null?void 0:p.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: {
    value: "Search query"
  }
}`,...(c=(m=r.parameters)==null?void 0:m.docs)==null?void 0:c.source}}};var l,i,u;o.parameters={...o.parameters,docs:{...(l=o.parameters)==null?void 0:l.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VSearchBar
    },
    setup() {
      const text = ref("Hello, World!");
      const updateText = (event: Event) => {
        const target = (event.target as HTMLInputElement);
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
}`,...(u=(i=o.parameters)==null?void 0:i.docs)==null?void 0:u.source}}};var d,h,f;a.parameters={...a.parameters,docs:{...(d=a.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "With placeholder",
  args: {
    placeholder: "Search query"
  }
}`,...(f=(h=a.parameters)==null?void 0:h.docs)==null?void 0:f.source}}};const oe=["Default","VModel","WithPlaceholder"];export{r as Default,o as VModel,a as WithPlaceholder,oe as __namedExportsOrder,re as default};
