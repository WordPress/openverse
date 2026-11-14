import{_ as n}from"./CH85vOLV.js";import{V as r}from"./9Q23NzEb.js";import{h as o}from"./lKNUlTH_.js";import"./CPKoWrgC.js";import"./DQnMOLSw.js";import"./CzMkt2mC.js";import"./C0voMBC3.js";import"./xwskLidM.js";import"./CFMQYC2y.js";import"./DMoasVxc.js";import"./C67TMzvP.js";import"./DYkE03l5.js";import"./fl49u9nx.js";import"./BOX21o1p.js";import"./CA4HNXs5.js";import"./CIg47mny.js";import"./MXhTc5uu.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";const g=["top","top-start","top-end","bottom","bottom-start","bottom-end","left","left-start","left-end","right","right-start","right-end"],K={title:"Components/VPopover",components:n,argTypes:{hideOnEsc:{control:{type:"boolean"}},hideOnClickOutside:{control:{type:"boolean"}},autoFocusOnShow:{control:{type:"boolean"}},autoFocusOnHide:{control:{type:"boolean"}},placement:{options:[...g],control:{type:"radio"}},label:{control:{type:"text"}},labelledBy:{control:{type:"text"}},onClose:{action:"close"},onOpen:{action:"open"},popoverItems:{control:{type:"number"}}},args:{id:"popover-story",hideOnEsc:!0,hideOnClickOutside:!0,autoFocusOnShow:!0,autoFocusOnHide:!0,placement:"bottom",label:"Code is Poetry",labelledBy:"popover-story"}},O=e=>({components:{VPopover:n,VButton:r},setup(){return()=>o("div",[o("p","This story is configured to log when the popover opens or closes. Inspect the Actions tab to observe this behavior."),o("div",{tabindex:"0"},"Focusable external area"),...Array(e.popoverItems).fill().map((t,i)=>o(n,{...e,key:i,class:"mb-2",onClose:e.onClose,onOpen:e.onOpen},{trigger:({visible:l,a11yProps:h})=>o(r,{pressed:l,variant:"filled-pink-8",size:"medium",...h},()=>l?"Close":"Open"),default:()=>o("div",{class:"py-1 px-2"},"Code is Poetry")}))])}}),P=e=>({components:{VPopover:n,VButton:r},setup(){return()=>o(n,{...e,onClose:e.onClose,onOpen:e.onOpen},{trigger:({visible:t,a11yProps:i})=>o(r,{pressed:t,variant:"filled-pink-8",size:"medium",...i},()=>t?"Close":"Open"),default:({close:t})=>o("div",{class:"p-4"},[o(r,{variant:"filled-gray",size:"medium",onClick:t},()=>"Close popover")])})}}),s={render:O.bind({}),name:"Default",args:{popoverItems:1}},p={render:P.bind({}),name:"Control"},a={render:O.bind({}),name:"Two Popovers",args:{popoverItems:2}};var m,c,d;s.parameters={...s.parameters,docs:{...(m=s.parameters)==null?void 0:m.docs,source:{originalSource:`{
  render: DefaultPopoverStory.bind({}),
  name: "Default",
  args: {
    popoverItems: 1
  }
}`,...(d=(c=s.parameters)==null?void 0:c.docs)==null?void 0:d.source}}};var u,v,y;p.parameters={...p.parameters,docs:{...(u=p.parameters)==null?void 0:u.docs,source:{originalSource:`{
  render: ControlStory.bind({}),
  name: "Control"
}`,...(y=(v=p.parameters)==null?void 0:v.docs)==null?void 0:y.source}}};var b,f,C;a.parameters={...a.parameters,docs:{...(b=a.parameters)==null?void 0:b.docs,source:{originalSource:`{
  render: DefaultPopoverStory.bind({}),
  name: "Two Popovers",
  args: {
    popoverItems: 2
  }
}`,...(C=(f=a.parameters)==null?void 0:f.docs)==null?void 0:C.source}}};const L=["Default","Control","TwoPopovers"];export{p as Control,s as Default,a as TwoPopovers,L as __namedExportsOrder,K as default};
