import{h as t}from"./53SD24Bo.js";import{b as d,a as u}from"./DdsKsgOu.js";import{W as f}from"./DOutFQEH.js";import{_ as r}from"./xQ8_qGND.js";import"./_bbq3c9C.js";import"./dvXbmdTd.js";import"./ivjvpZKc.js";import"./DjsporFN.js";import"./DhTbjJlp.js";import"./DlboKt2a.js";import"./Di7dAt70.js";import"./B9k6C3Hw.js";import"./BOewZ2sR.js";import"./D2GrBf-6.js";import"./B_-6Taiq.js";import"./CH5-dTGy.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="54da924b-edcf-4437-8ba1-da2f1ed2268e",e._sentryDebugIdIdentifier="sentry-dbid-54da924b-edcf-4437-8ba1-da2f1ed2268e")}catch{}})();const A={title:"Components/VIconButton",component:r,decorators:[f],argTypes:{size:{options:d,control:"select"},variant:{options:u,control:"select"}}},o={render:e=>({components:{VIconButton:r},setup(){return()=>t(r,{...e})}}),name:"Default",args:{variant:"filled-dark",size:"medium",label:"v-icon-button",iconProps:{name:"replay"}}},a={render:e=>({components:{VIconButton:r},setup(){return()=>t("div",{class:"flex gap-x-2"},d.map(n=>t("div",{class:"flex flex-col items-center p-2 gap-2"},[t("p",{class:"label-bold"},n),t(r,{...e,size:n},[])])))}}),name:"Sizes",args:{variant:"filled-dark",size:"small",label:"v-icon-button",iconProps:{name:"replay"}}};var s,i,l;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
}`,...(l=(i=o.parameters)==null?void 0:i.docs)==null?void 0:l.source}}};var p,c,m;a.parameters={...a.parameters,docs:{...(p=a.parameters)==null?void 0:p.docs,source:{originalSource:`{
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
}`,...(m=(c=a.parameters)==null?void 0:c.docs)==null?void 0:m.source}}};const C=["Default","Sizes"];export{o as Default,a as Sizes,C as __namedExportsOrder,A as default};
