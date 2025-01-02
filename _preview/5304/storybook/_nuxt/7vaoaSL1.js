import{b as d,a as u}from"./DBm0wiCE.js";import{W as f}from"./CyQJUNG1.js";import{_ as r}from"./XWxx7e39.js";import"./DJiKieMK.js";import{h as t}from"./Bf-AzR54.js";import"./cGIRWP1M.js";import"./BAvHRt8K.js";import"./BgVAWI2R.js";import"./DhTbjJlp.js";import"./BtGsfS_x.js";import"./CdpvutFv.js";import"./BHCnpuXR.js";import"./Cyf2jyE0.js";import"./DcwCHNwG.js";import"./qA--S04K.js";import"../sb-preview/runtime.js";(function(){try{var n=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},e=new n.Error().stack;e&&(n._sentryDebugIds=n._sentryDebugIds||{},n._sentryDebugIds[e]="6bd1a9a5-f013-438a-af4f-3dcd34938c5f",n._sentryDebugIdIdentifier="sentry-dbid-6bd1a9a5-f013-438a-af4f-3dcd34938c5f")}catch{}})();const W={title:"Components/VIconButton",component:r,decorators:[f],argTypes:{size:{options:d,control:"select"},variant:{options:u,control:"select"}}},o={render:n=>({components:{VIconButton:r},setup(){return()=>t(r,{...n})}}),name:"Default",args:{variant:"filled-dark",size:"medium",label:"v-icon-button",iconProps:{name:"replay"}}},a={render:n=>({components:{VIconButton:r},setup(){return()=>t("div",{class:"flex gap-x-2"},d.map(e=>t("div",{class:"flex flex-col items-center p-2 gap-2"},[t("p",{class:"label-bold"},e),t(r,{...n,size:e},[])])))}}),name:"Sizes",args:{variant:"filled-dark",size:"small",label:"v-icon-button",iconProps:{name:"replay"}}};var s,i,l;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(l=(i=o.parameters)==null?void 0:i.docs)==null?void 0:l.source}}};var c,p,m;a.parameters={...a.parameters,docs:{...(c=a.parameters)==null?void 0:c.docs,source:{originalSource:`{
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
}`,...(m=(p=a.parameters)==null?void 0:p.docs)==null?void 0:m.source}}};const A=["Default","Sizes"];export{o as Default,a as Sizes,A as __namedExportsOrder,W as default};
