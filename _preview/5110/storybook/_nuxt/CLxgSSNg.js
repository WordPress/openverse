import{W as A}from"./Bb8FjLK_.js";import{V as m}from"./CAhZsXLM.js";import{_ as r}from"./4ma1ifP_.js";import"./DUksCy1Q.js";import{D as w,h as n}from"./Bf-AzR54.js";import"./BEmSFkVT.js";import"./8Pdn1Bl1.js";import"./DhTbjJlp.js";import"./D9JVarWf.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},a=new e.Error().stack;a&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[a]="382484a9-aa77-46d8-aa3d-ef5c8c9757a6",e._sentryDebugIdIdentifier="sentry-dbid-382484a9-aa77-46d8-aa3d-ef5c8c9757a6")}catch{}})();const t={fieldId:"fruit",blankText:"Fruit",labelText:"Fruit",choices:[{key:"a",text:"Apple"},{key:"b",text:"Banana"},{key:"c",text:"Cantaloupe"}]},j={title:"Components/VSelectField",component:r,decorators:[A],argTypes:{"onUpdate:modelValue":{action:"update:modelValue"}}},v={render:e=>({components:{VSelectField:r},setup(){return()=>n(r,e)}}),args:{}},o={...v,name:"Default",args:t},s={...v,name:"Without border",args:{...t,variant:"borderless"}},c={render:e=>({components:{VSelectField:r},setup(){const a=w("a");return()=>n("div",[n(r,{...e,modelValue:a.value}),a.value])}}),name:"v-model",args:t},i={render:e=>({components:{VSelectField:r,VIcon:m},setup(){return()=>n(r,e,{start:()=>n(m,{name:"radiomark"})})}}),name:"With icon",args:t},d={render:e=>({components:{VSelectField:r,VIcon:m},setup(){return()=>n(r,{...e,class:"max-w-[100px]"},{start:()=>n(m,{name:"radiomark"})})}}),name:"With constraints",args:{...t,choices:[{key:"short",text:"Kiwi"},{key:"long",text:"Bob Gordon American Elderberry"}]}};var l,p,u;o.parameters={...o.parameters,docs:{...(l=o.parameters)==null?void 0:l.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: baseArgs
}`,...(u=(p=o.parameters)==null?void 0:p.docs)==null?void 0:u.source}}};var g,h,f;s.parameters={...s.parameters,docs:{...(g=s.parameters)==null?void 0:g.docs,source:{originalSource:`{
  ...Template,
  name: "Without border",
  args: {
    ...baseArgs,
    variant: "borderless"
  }
}`,...(f=(h=s.parameters)==null?void 0:h.docs)==null?void 0:f.source}}};var b,V,y;c.parameters={...c.parameters,docs:{...(b=c.parameters)==null?void 0:b.docs,source:{originalSource:`{
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
}`,...(y=(V=c.parameters)==null?void 0:V.docs)==null?void 0:y.source}}};var S,x,W;i.parameters={...i.parameters,docs:{...(S=i.parameters)==null?void 0:S.docs,source:{originalSource:`{
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
}`,...(W=(x=i.parameters)==null?void 0:x.docs)==null?void 0:W.source}}};var k,F,I;d.parameters={...d.parameters,docs:{...(k=d.parameters)==null?void 0:k.docs,source:{originalSource:`{
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
}`,...(I=(F=d.parameters)==null?void 0:F.docs)==null?void 0:I.source}}};const q=["Default","WithoutBorder","VModel","WithIcon","WithConstraints"];export{o as Default,c as VModel,d as WithConstraints,i as WithIcon,s as WithoutBorder,q as __namedExportsOrder,j as default};
