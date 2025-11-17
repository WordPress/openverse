import{h as t}from"./53SD24Bo.js";import{b as d,a as u}from"./pVa3tHja.js";import{W as f}from"./D3RHUH_N.js";import{_ as r}from"./C0eb6efW.js";import"./Bk8VSEei.js";import"./CQ3yco75.js";import"./b8e1KD_n.js";import"./C7m8LBdt.js";import"./DhTbjJlp.js";import"./Cpzk_0_B.js";import"./Bl5m8s2n.js";import"./DLXib-Qm.js";import"./Cbq1TCLb.js";import"./fL1fV1YB.js";import"./D1l3oJXo.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},n=new e.Error().stack;n&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[n]="c2967eda-0e79-4e87-961c-c717dd0a95a2",e._sentryDebugIdIdentifier="sentry-dbid-c2967eda-0e79-4e87-961c-c717dd0a95a2")}catch{}})();const W={title:"Components/VIconButton",component:r,decorators:[f],argTypes:{size:{options:d,control:"select"},variant:{options:u,control:"select"}}},o={render:e=>({components:{VIconButton:r},setup(){return()=>t(r,{...e})}}),name:"Default",args:{variant:"filled-dark",size:"medium",label:"v-icon-button",iconProps:{name:"replay"}}},a={render:e=>({components:{VIconButton:r},setup(){return()=>t("div",{class:"flex gap-x-2"},d.map(n=>t("div",{class:"flex flex-col items-center p-2 gap-2"},[t("p",{class:"label-bold"},n),t(r,{...e,size:n},[])])))}}),name:"Sizes",args:{variant:"filled-dark",size:"small",label:"v-icon-button",iconProps:{name:"replay"}}};var s,i,c;o.parameters={...o.parameters,docs:{...(s=o.parameters)==null?void 0:s.docs,source:{originalSource:`{
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
