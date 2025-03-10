import{r as A,h as n}from"./53SD24Bo.js";import{W as w}from"./Djp33N3D.js";import{V as m}from"./CxzE6WfI.js";import{_ as r}from"./zrJmgcCO.js";import"./RQxsyxdU.js";import"./BsOxdBIg.js";import"./C4QhmNcb.js";import"./DhTbjJlp.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="a64cfbc4-8b5f-40f5-ab09-6f6f68da9bdd",e._sentryDebugIdIdentifier="sentry-dbid-a64cfbc4-8b5f-40f5-ab09-6f6f68da9bdd")}catch{}})();const a={fieldId:"fruit",blankText:"Fruit",labelText:"Fruit",choices:[{key:"a",text:"Apple"},{key:"b",text:"Banana"},{key:"c",text:"Cantaloupe"}]},U={title:"Components/VSelectField",component:r,decorators:[w],argTypes:{"onUpdate:modelValue":{action:"update:modelValue"}}},v={render:e=>({components:{VSelectField:r},setup(){return()=>n(r,e)}}),args:{}},o={...v,name:"Default",args:a},s={...v,name:"Without border",args:{...a,variant:"borderless"}},c={render:e=>({components:{VSelectField:r},setup(){const t=A("a");return()=>n("div",[n(r,{...e,modelValue:t.value}),t.value])}}),name:"v-model",args:a},d={render:e=>({components:{VSelectField:r,VIcon:m},setup(){return()=>n(r,e,{start:()=>n(m,{name:"radiomark"})})}}),name:"With icon",args:a},i={render:e=>({components:{VSelectField:r,VIcon:m},setup(){return()=>n(r,{...e,class:"max-w-[100px]"},{start:()=>n(m,{name:"radiomark"})})}}),name:"With constraints",args:{...a,choices:[{key:"short",text:"Kiwi"},{key:"long",text:"Bob Gordon American Elderberry"}]}};var l,p,u;o.parameters={...o.parameters,docs:{...(l=o.parameters)==null?void 0:l.docs,source:{originalSource:`{
  ...Template,
  name: "Default",
  args: baseArgs
}`,...(u=(p=o.parameters)==null?void 0:p.docs)==null?void 0:u.source}}};var g,f,b;s.parameters={...s.parameters,docs:{...(g=s.parameters)==null?void 0:g.docs,source:{originalSource:`{
  ...Template,
  name: "Without border",
  args: {
    ...baseArgs,
    variant: "borderless"
  }
}`,...(b=(f=s.parameters)==null?void 0:f.docs)==null?void 0:b.source}}};var h,V,y;c.parameters={...c.parameters,docs:{...(h=c.parameters)==null?void 0:h.docs,source:{originalSource:`{
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
}`,...(y=(V=c.parameters)==null?void 0:V.docs)==null?void 0:y.source}}};var S,x,W;d.parameters={...d.parameters,docs:{...(S=d.parameters)==null?void 0:S.docs,source:{originalSource:`{
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
}`,...(W=(x=d.parameters)==null?void 0:x.docs)==null?void 0:W.source}}};var k,F,I;i.parameters={...i.parameters,docs:{...(k=i.parameters)==null?void 0:k.docs,source:{originalSource:`{
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
}`,...(I=(F=i.parameters)==null?void 0:F.docs)==null?void 0:I.source}}};const j=["Default","WithoutBorder","VModel","WithIcon","WithConstraints"];export{o as Default,c as VModel,i as WithConstraints,d as WithIcon,s as WithoutBorder,j as __namedExportsOrder,U as default};
