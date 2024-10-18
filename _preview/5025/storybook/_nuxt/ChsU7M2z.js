import{b as u,a as d}from"./CUw4t6IM.js";import{W as f}from"./8JpoR7ar.js";import{_ as e}from"./Do2yKSxf.js";import{h as n}from"./lnpB3OcH.js";import"./ZjNmaQpL.js";import"./CuPsdpTl.js";import"./CFMQYC2y.js";import"./DlAUqK2U.js";import"./DuVMw8T-.js";import"./BvLt3-_D.js";import"./BNurbrIm.js";import"./BOX21o1p.js";import"./CtE17snF.js";import"./D-c0xjtQ.js";const P={title:"Components/VIconButton",component:e,decorators:[f],argTypes:{size:{options:u,control:"select"},variant:{options:d,control:"select"}}},o={render:t=>({components:{VIconButton:e},setup(){return()=>n(e,{...t})}}),name:"Default",args:{variant:"filled-dark",size:"medium",label:"v-icon-button",iconProps:{name:"replay"}}},r={render:t=>({components:{VIconButton:e},setup(){return()=>n("div",{class:"flex gap-x-2"},u.map(a=>n("div",{class:"flex flex-col items-center p-2 gap-2"},[n("p",{class:"label-bold"},a),n(e,{...t,size:a},[])])))}}),name:"Sizes",args:{variant:"filled-dark",size:"small",label:"v-icon-button",iconProps:{name:"replay"}}};var s,i,l;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VIconButton
    },
    setup() {
      return () => h(VIconButton, {
        ...args
      });
    }
  }),
  name: "Default",
  args: {
    variant: "filled-dark",
    size: "medium",
    label: "v-icon-button",
    iconProps: {
      name: "replay"
    }
  }
}`,...(l=(i=o.parameters)==null?void 0:i.docs)==null?void 0:l.source}}};var p,c,m;r.parameters={...r.parameters,docs:{...(p=r.parameters)==null?void 0:p.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VIconButton
    },
    setup() {
      return () => h("div", {
        class: "flex gap-x-2"
      }, baseButtonSizes.map(size => h("div", {
        class: "flex flex-col items-center p-2 gap-2"
      }, [h("p", {
        class: "label-bold"
      }, size), h(VIconButton, {
        ...args,
        size
      }, [])])));
    }
  }),
  name: "Sizes",
  args: {
    variant: "filled-dark",
    size: "small",
    label: "v-icon-button",
    iconProps: {
      name: "replay"
    }
  }
}`,...(m=(c=r.parameters)==null?void 0:c.docs)==null?void 0:m.source}}};const W=["Default","Sizes"];export{o as Default,r as Sizes,W as __namedExportsOrder,P as default};
