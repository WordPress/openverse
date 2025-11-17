import{h as t}from"./DwwldUEF.js";import{b as d,a as u}from"./Cot9uS2b.js";import{W as f}from"./r7DnlIPq.js";import{_ as r}from"./CUCjtGpu.js";import"./CWoQmekT.js";import"./DoSYsHAz.js";import"./aezMCrU2.js";import"./tAHCZdDM.js";import"./DhTbjJlp.js";import"./Dhs1Or-2.js";import"./CUvT7aun.js";import"./TLA9Fm80.js";import"./DqyB4W5h.js";import"./BtS8wA1z.js";import"./VcnMPoS3.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="c2967eda-0e79-4e87-961c-c717dd0a95a2",e._sentryDebugIdIdentifier="sentry-dbid-c2967eda-0e79-4e87-961c-c717dd0a95a2")}catch{}})();const W={title:"Components/VIconButton",component:r,decorators:[f],argTypes:{size:{options:d,control:"select"},variant:{options:u,control:"select"}}},o={render:e=>({components:{VIconButton:r},setup(){return()=>t(r,{...e})}}),name:"Default",args:{variant:"filled-dark",size:"medium",label:"v-icon-button",iconProps:{name:"replay"}}},a={render:e=>({components:{VIconButton:r},setup(){return()=>t("div",{class:"flex gap-x-2"},d.map(n=>t("div",{class:"flex flex-col items-center p-2 gap-2"},[t("p",{class:"label-bold"},n),t(r,{...e,size:n},[])])))}}),name:"Sizes",args:{variant:"filled-dark",size:"small",label:"v-icon-button",iconProps:{name:"replay"}}};var s,i,c;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(m=(p=a.parameters)==null?void 0:p.docs)==null?void 0:m.source}}};const A=["Default","Sizes"];export{o as Default,a as Sizes,A as __namedExportsOrder,W as default};
