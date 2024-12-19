import{c as _}from"./uHJqFrjm.js";import{c as C,d,e as W}from"./B9lLXRL8.js";import{V as r}from"./2X7CKgv5.js";import{V as s}from"./sL22Kbl4.js";import"./DzKe1FZy.js";import{h as n}from"./Bf-AzR54.js";import"./DJpKulq8.js";import"./RE842jSx.js";import"./Mi53UD0-.js";import"./BdGbGJtZ.js";import"./KaIp0RKv.js";import"./Imyqroa4.js";import"./DhTbjJlp.js";import"./CYExI-7Z.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},t=new e.Error().stack;t&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[t]="0f8e435d-5c26-4710-9bfd-6a02ace0c99a",e._sentryDebugIdIdentifier="sentry-dbid-0f8e435d-5c26-4710-9bfd-6a02ace0c99a")}catch{}})();const u={filled:d.filter(e=>e.startsWith("filled-")),bordered:d.filter(e=>e.startsWith("bordered-")),transparent:d.filter(e=>e.startsWith("transparent-"))},X={title:"Components/VButton",component:r,parameters:{viewport:{defaultViewport:"sm"}},args:{size:"medium"},argTypes:{as:{options:C,control:{type:"radio"}},variant:{options:d,control:{type:"select"}},pressed:{control:"boolean"},size:{options:W,control:{type:"select"}},disabled:{control:"boolean"},focusableWhenDisabled:{control:"boolean"},type:{control:"text"},onClick:{action:"click"},onMouseDown:{action:"mousedown"},onKeydown:{action:"keydown"},onFocus:{action:"focus"},onBlur:{action:"blur"}}},F=e=>({components:{VButton:r},setup(){const{size:t,variant:a,...o}=e;return()=>n("div",{class:"flex"},[n("div",{id:"wrapper",class:["px-4 h-16 flex items-center justify-center",a.startsWith("transparent")?"bg-surface":"bg-default"]},[n(r,{size:t,variant:a,class:"description-bold",href:"/",...o},()=>"Code is Poetry")])])}}),A=e=>({components:{VButton:r,VIcon:s},setup(){return()=>n("div",{class:"flex flex-col items-center gap-4 flex-wrap"},[n(r,{variant:e.variant,size:e.size,"has-icon-start":!0},()=>[n(s,{name:"replay"}),"Button"]),n(r,{variant:e.variant,size:e.size,"has-icon-end":!0},()=>["Button",n(s,{name:"external-link"})]),n(r,{variant:e.variant,size:e.size,"has-icon-start":!0,"has-icon-end":!0},()=>[n(s,{name:"replay"}),"Button",n(s,{name:"external-link"})])])}}),b=e=>({components:{VButton:r},setup(){const{variants:t,...a}=e;return()=>n("div",{class:"flex gap-4 flex-wrap"},t.map(o=>n(r,{variant:o,key:o,class:"description-bold",...a},()=>_(o))))}}),c={render:F.bind({}),name:"VButton",args:{variant:"filled-pink-8"}},i=b.bind({});i.args={variants:u.filled};const p={render:b.bind({}),name:"bordered",args:{variants:u.bordered}},l={render:b.bind({}),name:"transparent",args:{variants:u.transparent}},m={render:A.bind({}),name:"icons",args:{variant:"bordered-dark"},argTypes:{pressed:{control:"boolean"},size:{options:W,control:{type:"radio"}},variant:{options:d},disabled:{control:"boolean"}}};var f,v,g;c.parameters={...c.parameters,docs:{...(f=c.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "VButton",
  args: {
    variant: "filled-pink-8"
  }
}`,...(g=(v=c.parameters)==null?void 0:v.docs)==null?void 0:g.source}}};var y,V,h;i.parameters={...i.parameters,docs:{...(y=i.parameters)==null?void 0:y.docs,source:{originalSource:`args => ({
  components: {
    VButton
  },
  setup() {
    const {
      variants,
      ...buttonArgs
    } = args;
    return () => h("div", {
      class: "flex gap-4 flex-wrap"
    }, variants.map(variant => h(VButton, {
      variant,
      key: variant,
      class: "description-bold",
      ...buttonArgs
    }, () => capitalCase(variant))));
  }
})`,...(h=(V=i.parameters)==null?void 0:V.docs)==null?void 0:h.source}}};var w,x,z;p.parameters={...p.parameters,docs:{...(w=p.parameters)==null?void 0:w.docs,source:{originalSource:`{
  render: VariantsTemplate.bind({}),
  name: "bordered",
  args: {
    variants: buttonVariantGroups.bordered
  }
}`,...(z=(x=p.parameters)==null?void 0:x.docs)==null?void 0:z.source}}};var B,k,T;l.parameters={...l.parameters,docs:{...(B=l.parameters)==null?void 0:B.docs,source:{originalSource:`{
  render: VariantsTemplate.bind({}),
  name: "transparent",
  args: {
    variants: buttonVariantGroups.transparent
  }
}`,...(T=(k=l.parameters)==null?void 0:k.docs)==null?void 0:T.source}}};var I,D,S;m.parameters={...m.parameters,docs:{...(I=m.parameters)==null?void 0:I.docs,source:{originalSource:`{
  render: TemplateWithIcons.bind({}),
  name: "icons",
  args: {
    variant: "bordered-dark"
  },
  argTypes: {
    pressed: {
      control: "boolean"
    },
    size: {
      options: buttonSizes,
      control: {
        type: "radio"
      }
    },
    variant: {
      options: buttonVariants
    },
    disabled: {
      control: "boolean"
    }
  }
}`,...(S=(D=m.parameters)==null?void 0:D.docs)==null?void 0:S.source}}};const Y=["Default","Filled","Bordered","Transparent","Icons"];export{p as Bordered,c as Default,i as Filled,m as Icons,l as Transparent,Y as __namedExportsOrder,X as default};
