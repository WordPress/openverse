import{c as D,d as s,e as I}from"./CUw4t6IM.js";import{a as F}from"./D0ww02ZN.js";import{V as r}from"./BY12SjvE.js";import{V as a}from"./BdoT2ima.js";import{h as e}from"./B18F2_lz.js";import"./9FKpjZKd.js";import"./CFYL8r3V.js";import"./CFMQYC2y.js";import"./BOX21o1p.js";import"./_dzyiV2Y.js";import"./BC9BnLXc.js";import"./DlAUqK2U.js";import"./CuPsdpTl.js";const u={filled:s.filter(n=>n.startsWith("filled-")),bordered:s.filter(n=>n.startsWith("bordered-")),transparent:s.filter(n=>n.startsWith("transparent-"))},R={title:"Components/VButton",component:r,parameters:{viewport:{defaultViewport:"sm"}},args:{size:"medium"},argTypes:{as:{options:D,control:{type:"radio"}},variant:{options:s,control:{type:"select"}},pressed:{control:"boolean"},size:{options:I,control:{type:"select"}},disabled:{control:"boolean"},focusableWhenDisabled:{control:"boolean"},type:{control:"text"},onClick:{action:"click"},onMouseDown:{action:"mousedown"},onKeydown:{action:"keydown"},onFocus:{action:"focus"},onBlur:{action:"blur"}}},A=n=>({components:{VButton:r},setup(){const{size:m,variant:i,...t}=n;return()=>e("div",{class:"flex"},[e("div",{id:"wrapper",class:["px-4 h-16 flex items-center justify-center",i.startsWith("transparent")?"bg-surface":"bg-default"]},[e(r,{size:m,variant:i,class:"description-bold",href:"/",...t},()=>"Code is Poetry")])])}}),G=n=>({components:{VButton:r,VIcon:a},setup(){return()=>e("div",{class:"flex flex-col items-center gap-4 flex-wrap"},[e(r,{variant:n.variant,size:n.size,"has-icon-start":!0},()=>[e(a,{name:"replay"}),"Button"]),e(r,{variant:n.variant,size:n.size,"has-icon-end":!0},()=>["Button",e(a,{name:"external-link"})]),e(r,{variant:n.variant,size:n.size,"has-icon-start":!0,"has-icon-end":!0},()=>[e(a,{name:"replay"}),"Button",e(a,{name:"external-link"})])])}}),b=n=>({components:{VButton:r},setup(){const{variants:m,...i}=n;return()=>e("div",{class:"flex gap-4 flex-wrap"},m.map(t=>e(r,{variant:t,key:t,class:"description-bold",...i},()=>F(t))))}}),p={render:A.bind({}),name:"VButton",args:{variant:"filled-pink-8"}},o=b.bind({});o.args={variants:u.filled};const c={render:b.bind({}),name:"bordered",args:{variants:u.bordered}},d={render:b.bind({}),name:"transparent",args:{variants:u.transparent}},l={render:G.bind({}),name:"icons",args:{variant:"bordered-dark"},argTypes:{pressed:{control:"boolean"},size:{options:I,control:{type:"radio"}},variant:{options:s},disabled:{control:"boolean"}}};var f,v,g;p.parameters={...p.parameters,docs:{...(f=p.parameters)==null?void 0:f.docs,source:{originalSource:`{
  render: Template.bind({}),
  name: "VButton",
  args: {
    variant: "filled-pink-8"
  }
}`,...(g=(v=p.parameters)==null?void 0:v.docs)==null?void 0:g.source}}};var V,y,h;o.parameters={...o.parameters,docs:{...(V=o.parameters)==null?void 0:V.docs,source:{originalSource:`args => ({
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
})`,...(h=(y=o.parameters)==null?void 0:y.docs)==null?void 0:h.source}}};var x,z,B;c.parameters={...c.parameters,docs:{...(x=c.parameters)==null?void 0:x.docs,source:{originalSource:`{
  render: VariantsTemplate.bind({}),
  name: "bordered",
  args: {
    variants: buttonVariantGroups.bordered
  }
}`,...(B=(z=c.parameters)==null?void 0:z.docs)==null?void 0:B.source}}};var T,k,w;d.parameters={...d.parameters,docs:{...(T=d.parameters)==null?void 0:T.docs,source:{originalSource:`{
  render: VariantsTemplate.bind({}),
  name: "transparent",
  args: {
    variants: buttonVariantGroups.transparent
  }
}`,...(w=(k=d.parameters)==null?void 0:k.docs)==null?void 0:w.source}}};var S,W,C;l.parameters={...l.parameters,docs:{...(S=l.parameters)==null?void 0:S.docs,source:{originalSource:`{
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
}`,...(C=(W=l.parameters)==null?void 0:W.docs)==null?void 0:C.source}}};const U=["Default","Filled","Bordered","Transparent","Icons"];export{c as Bordered,p as Default,o as Filled,l as Icons,d as Transparent,U as __namedExportsOrder,R as default};
