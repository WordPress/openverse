import{h as n}from"./53SD24Bo.js";import{c as _}from"./C-ucudUc.js";import{c as C,d as s,e as W}from"./Q73B2dTi.js";import{V as r}from"./ByZ6H8Q9.js";import{V as t}from"./CxzE6WfI.js";import"./RQxsyxdU.js";import"./oAL5f6fw.js";import"./Cai0IfA4.js";import"./B7ZxQ_gM.js";import"./CGdESDy3.js";import"./C4QhmNcb.js";import"./BALwooav.js";import"./DhTbjJlp.js";import"./BsOxdBIg.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},o=new e.Error().stack;o&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[o]="238ddbe5-a1da-4f9f-9c1e-4578c8c847dc",e._sentryDebugIdIdentifier="sentry-dbid-238ddbe5-a1da-4f9f-9c1e-4578c8c847dc")}catch{}})();const u={filled:s.filter(e=>e.startsWith("filled-")),bordered:s.filter(e=>e.startsWith("bordered-")),transparent:s.filter(e=>e.startsWith("transparent-"))},X={title:"Components/VButton",component:r,parameters:{viewport:{defaultViewport:"sm"}},args:{sSize:"medium"},argTypes:{as:{options:C,control:{type:"radio"}},sVariant:{options:s,control:{type:"select"}},sSize:{options:W,control:{type:"select"}},pressed:{control:"boolean"},disabled:{control:"boolean"},focusableWhenDisabled:{control:"boolean"},type:{control:"text"},onClick:{action:"click"},onMouseDown:{action:"mousedown"},onKeydown:{action:"keydown"},onFocus:{action:"focus"},onBlur:{action:"blur"}}},A=e=>({components:{VButton:r},setup(){return()=>n("div",{class:"flex"},[n("div",{id:"wrapper",class:["px-4 h-16 flex items-center justify-center",e.sVariant.startsWith("transparent")?"bg-surface":"bg-default"]},[n(r,{class:"description-bold",href:"/",...e,variant:e.sVariant,size:e.sSize},()=>"Code is Poetry")])])}}),F=e=>({components:{VButton:r,VIcon:t},setup(){return()=>n("div",{class:"flex flex-col items-center gap-4 flex-wrap"},[n(r,{variant:e.sVariant,size:e.sSize,"has-icon-start":!0},()=>[n(t,{name:"replay"}),"Button"]),n(r,{variant:e.sVariant,size:e.sSize,"has-icon-end":!0},()=>["Button",n(t,{name:"external-link"})]),n(r,{variant:e.sVariant,size:e.sSize,"has-icon-start":!0,"has-icon-end":!0},()=>[n(t,{name:"replay"}),"Button",n(t,{name:"external-link"})])])}}),b=e=>({components:{VButton:r},setup(){const{variants:o,...l}=e;return()=>n("div",{class:"flex gap-4 flex-wrap"},o.map(m=>n(r,{variant:m,key:m,class:"description-bold",...l,size:l.sSize},()=>_(m))))}}),i={render:A.bind({}),name:"VButton",args:{sVariant:"filled-pink-8"}},a=b.bind({});a.args={variants:u.filled};const d={render:b.bind({}),name:"bordered",args:{variants:u.bordered}},c={render:b.bind({}),name:"transparent",args:{variants:u.transparent}},p={render:F.bind({}),name:"icons",args:{sVariant:"bordered-dark"},argTypes:{pressed:{control:"boolean"},sSize:{options:W,control:{type:"radio"}},sVariant:{options:s},disabled:{control:"boolean"}}};var f,V,g;i.parameters={...i.parameters,docs:{...(f=i.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "VButton",
  args: {
    sVariant: "filled-pink-8"
  }
}`,...(g=(V=i.parameters)==null?void 0:V.docs)==null?void 0:g.source}}};var y,v,z;a.parameters={...a.parameters,docs:{...(y=a.parameters)==null?void 0:y.docs,source:{originalSource:`args => ({
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
      ...buttonArgs,
      size: buttonArgs.sSize
    }, () => capitalCase(variant))));
  }
})`,...(z=(v=a.parameters)==null?void 0:v.docs)==null?void 0:z.source}}};var h,S,w;d.parameters={...d.parameters,docs:{...(h=d.parameters)==null?void 0:h.docs,source:{originalSource:`{
  render: VariantsTemplate.bind({}),
  name: "bordered",
  args: {
    variants: buttonVariantGroups.bordered
  }
}`,...(w=(S=d.parameters)==null?void 0:S.docs)==null?void 0:w.source}}};var x,B,k;c.parameters={...c.parameters,docs:{...(x=c.parameters)==null?void 0:x.docs,source:{originalSource:`{
  render: VariantsTemplate.bind({}),
  name: "transparent",
  args: {
    variants: buttonVariantGroups.transparent
  }
}`,...(k=(B=c.parameters)==null?void 0:B.docs)==null?void 0:k.source}}};var T,I,D;p.parameters={...p.parameters,docs:{...(T=p.parameters)==null?void 0:T.docs,source:{originalSource:`{
  render: TemplateWithIcons.bind({}),
  name: "icons",
  args: {
    sVariant: "bordered-dark"
  },
  argTypes: {
    pressed: {
      control: "boolean"
    },
    sSize: {
      options: buttonSizes,
      control: {
        type: "radio"
      }
    },
    sVariant: {
      options: buttonVariants
    },
    disabled: {
      control: "boolean"
    }
  }
}`,...(D=(I=p.parameters)==null?void 0:I.docs)==null?void 0:D.source}}};const Y=["Default","Filled","Bordered","Transparent","Icons"];export{d as Bordered,i as Default,a as Filled,p as Icons,c as Transparent,Y as __namedExportsOrder,X as default};
