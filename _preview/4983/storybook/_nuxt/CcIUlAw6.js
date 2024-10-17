import{W as I}from"./mhLUjpuo.js";import{V as m}from"./BdoT2ima.js";import{_ as e}from"./CeqMdjdi.js";import{G as T,h as n}from"./B18F2_lz.js";import"./CuPsdpTl.js";import"./CFMQYC2y.js";import"./DlAUqK2U.js";import"./DuePtXgb.js";const a={fieldId:"fruit",blankText:"Fruit",labelText:"Fruit",choices:[{key:"a",text:"Apple"},{key:"b",text:"Banana"},{key:"c",text:"Cantaloupe"}]},M={title:"Components/VSelectField",component:e,decorators:[I],argTypes:{"onUpdate:modelValue":{action:"update:modelValue"}}},A={render:r=>({components:{VSelectField:e},setup(){return()=>n(e,r)}}),args:{}},t={...A,name:"Default",args:a},o={...A,name:"Without border",args:{...a,variant:"borderless"}},s={render:r=>({components:{VSelectField:e},setup(){const l=T("a");return()=>n("div",[n(e,{...r,modelValue:l.value}),l.value])}}),name:"v-model",args:a},c={render:r=>({components:{VSelectField:e,VIcon:m},setup(){return()=>n(e,r,{start:()=>n(m,{name:"radiomark"})})}}),name:"With icon",args:a},i={render:r=>({components:{VSelectField:e,VIcon:m},setup(){return()=>n(e,{...r,class:"max-w-[100px]"},{start:()=>n(m,{name:"radiomark"})})}}),name:"With constraints",args:{...a,choices:[{key:"short",text:"Kiwi"},{key:"long",text:"Bob Gordon American Elderberry"}]}};var d,p,u;t.parameters={...t.parameters,docs:{...(d=t.parameters)==null?void 0:d.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: baseArgs
}`,...(u=(p=t.parameters)==null?void 0:p.docs)==null?void 0:u.source}}};var g,h,V;o.parameters={...o.parameters,docs:{...(g=o.parameters)==null?void 0:g.docs,source:{originalSource:`{
  ...Template,
  name: "Without border",
  args: {
    ...baseArgs,
    variant: "borderless"
  }
}`,...(V=(h=o.parameters)==null?void 0:h.docs)==null?void 0:V.source}}};var b,S,x;s.parameters={...s.parameters,docs:{...(b=s.parameters)==null?void 0:b.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VSelectField
    },
    setup() {
      const choice = ref("a");
      return () => h("div", [h(VSelectField, {
        ...args,
        modelValue: choice.value
      }), choice.value]);
    }
  }),
  name: "v-model",
  args: baseArgs
}`,...(x=(S=s.parameters)==null?void 0:S.docs)==null?void 0:x.source}}};var f,W,F;c.parameters={...c.parameters,docs:{...(f=c.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VSelectField,
      VIcon
    },
    setup() {
      return () => h(VSelectField, args, {
        start: () => h(VIcon, {
          name: "radiomark"
        })
      });
    }
  }),
  name: "With icon",
  args: baseArgs
}`,...(F=(W=c.parameters)==null?void 0:W.docs)==null?void 0:F.source}}};var k,v,y;i.parameters={...i.parameters,docs:{...(k=i.parameters)==null?void 0:k.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VSelectField,
      VIcon
    },
    setup() {
      return () => h(VSelectField, {
        ...args,
        class: "max-w-[100px]"
      }, {
        start: () => h(VIcon, {
          name: "radiomark"
        })
      });
    }
  }),
  name: "With constraints",
  args: {
    ...baseArgs,
    choices: [{
      key: "short",
      text: "Kiwi"
    }, {
      key: "long",
      text: "Bob Gordon American Elderberry"
    }]
  }
}`,...(y=(v=i.parameters)==null?void 0:v.docs)==null?void 0:y.source}}};const O=["Default","WithoutBorder","VModel","WithIcon","WithConstraints"];export{t as Default,s as VModel,i as WithConstraints,c as WithIcon,o as WithoutBorder,O as __namedExportsOrder,M as default};
