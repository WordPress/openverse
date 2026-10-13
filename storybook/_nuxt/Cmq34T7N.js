import{h as t}from"./DmrXErv4.js";import{b as u,a as d}from"./Co0ITW6D.js";import{W as f}from"./DSgSzK8z.js";import{_ as r}from"./us_YXsMU.js";import"./Ceavzuo-.js";import"./CdX5GYQk.js";import"./qy-jYTsH.js";import"./BayljJpb.js";import"./DhTbjJlp.js";import"./0xbGHjBU.js";import"./lCCmDL6e.js";import"./Dp2jPxn_.js";import"./CtkidDXQ.js";import"./CMZS2cOm.js";import"./BS_ZT77X.js";import"./Ck0gvfbg.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="4cf51af9-c71b-4e11-9dbe-7822d5e9e6c3",e._sentryDebugIdIdentifier="sentry-dbid-4cf51af9-c71b-4e11-9dbe-7822d5e9e6c3")}catch{}})();const A={title:"Components/VIconButton",component:r,decorators:[f],argTypes:{size:{options:d,control:"select"},variant:{options:u,control:"select"}}},o={render:e=>({components:{VIconButton:r},setup(){return()=>t(r,{...e})}}),name:"Default",args:{variant:"filled-dark",size:"medium",label:"v-icon-button",iconProps:{name:"replay"}}},a={render:e=>({components:{VIconButton:r},setup(){return()=>t("div",{class:"flex gap-x-2"},d.map(n=>t("div",{class:"flex flex-col items-center p-2 gap-2"},[t("p",{class:"label-bold"},n),t(r,{...e,size:n},[])])))}}),name:"Sizes",args:{variant:"filled-dark",size:"small",label:"v-icon-button",iconProps:{name:"replay"}}};var s,i,c;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(c=(i=o.parameters)==null?void 0:i.docs)==null?void 0:c.source}}};var l,p,m;a.parameters={...a.parameters,docs:{...(l=a.parameters)==null?void 0:l.docs,source:{originalSource:`{
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
}`,...(m=(p=a.parameters)==null?void 0:p.docs)==null?void 0:m.source}}};const C=["Default","Sizes"];export{o as Default,a as Sizes,C as __namedExportsOrder,A as default};
