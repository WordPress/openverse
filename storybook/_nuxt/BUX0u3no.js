import{r as g,h as r}from"./DmrXErv4.js";import{V as d,_ as l,i as G}from"./DHG5U8zu.js";import{V as m}from"./CdX5GYQk.js";import{_ as I}from"./T3zie1aL.js";import{V as f}from"./0xbGHjBU.js";import"./Ceavzuo-.js";import"./CVvkZ7Vc.js";import"./C4vooYs6.js";import"./BS_ZT77X.js";import"./S_btu43D.js";import"./Dp2jPxn_.js";import"./DhTbjJlp.js";import"./qy-jYTsH.js";import"./BayljJpb.js";import"./Dp_7e0gy.js";import"./BxtqxG2r.js";import"./DtBeafs8.js";import"./DIkXdRcj.js";import"./lCCmDL6e.js";import"./CtkidDXQ.js";import"./CMZS2cOm.js";import"./Ck0gvfbg.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},s=new e.Error().stack;s&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[s]="32545355-2fb9-4924-bb85-7f837ac8e785",e._sentryDebugIdIdentifier="sentry-dbid-32545355-2fb9-4924-bb85-7f837ac8e785")}catch{}})();const Z={title:"Components/VItemGroup",component:l,subcomponents:{VItem:d,VIcon:m,VPopover:I,VButton:f},argTypes:{direction:{options:G,control:{type:"radio"}},bordered:{control:{type:"boolean"}}}},P='This is a "menu" style item group. Multiple items can be active at a time and all have the "menuitemcheckbox" role.',k=(e,s,i)=>r(d,{key:e.id,selected:i.value.id===e.id,isFirst:s===0,onClick:()=>{i.value=e},size:"medium"},{default:()=>[r(m,{name:e.icon}),r("span",{},e.label)]}),D=(e,s,i,t,a)=>r(d,{key:e.id,selected:i.value.has(e.id),isFirst:s===0,onClick:()=>t(e),size:"medium"},{default:()=>[r(m,{name:e.icon}),r("span",{class:a==="horizontal"?"pe-2":""},e.label)]}),p={render:e=>({components:{VItemGroup:l,VItem:d,VIcon:m},setup(){const s=["close","pause","play","replay"],i=new Array(s.length).fill(null).map((a,n)=>({id:n,label:`Item ${n}`,icon:s[n]})),t=g({});return()=>r("div",{},[r("p",{},'This is a "radio" style list group. Only a single element can be selected at a time.'),r("div",{style:"width: 300px"},[r(l,{...e,type:"radiogroup"},{default:()=>i.map((a,n)=>k(a,n,t))})])])}}),name:"Default",args:{direction:"vertical",bordered:!0}},c={render:e=>({components:{VItemGroup:l,VItem:d,VIcon:m},setup(){const s=["close","pause","play","replay"],i=new Array(s.length).fill(null).map((n,o)=>({id:o,label:`Item ${o}`,icon:s[o]})),t=g(new Set),a=n=>{t.value.delete(n.id)?t.value=new Set(t.value):t.value=new Set(t.value.add(n.id))};return()=>r("div",{},[r("p",{},P),r("div",{style:"width: 300px"},[r(l,{...e,type:"menu"},{default:()=>i.map((n,o)=>D(n,o,t,a))})])])}}),name:"Menu",args:{direction:"vertical",bordered:!0}},u={render:e=>({components:{VButton:f,VPopover:I,VItem:d,VItemGroup:l,VIcon:m},setup(){const s=["close","pause","play","replay"],i=new Array(s.length).fill(null).map((n,o)=>({id:o,label:`Item ${o}`,icon:s[o]})),t=g(new Set),a=n=>{t.value.delete(n.id)?t.value=new Set(t.value):t.value=new Set(t.value.add(n.id))};return()=>r(I,{id:"item-group-popover"},{trigger:({a11yProps:n,visible:o})=>r(f,{variant:"filled-pink-8",size:"medium",...n,pressed:o},{default:()=>o?"Close menu":"Open menu"}),default:()=>[r(l,{...e,type:"menu"},{default:()=>i.map((n,o)=>D(n,o,t,a,e.direction))})]})}}),name:"Popover",args:{direction:"vertical",bordered:!1}};var v,y,b;p.parameters={...p.parameters,docs:{...(v=p.parameters)==null?void 0:v.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VItemGroup,
      VItem,
      VIcon
    },
    setup() {
      const icons = ["close", "pause", "play", "replay"];
      const items = new Array(icons.length).fill(null).map((_, i) => ({
        id: i,
        label: \`Item \${i}\`,
        icon: icons[i]
      }));
      const selectedItem = ref({} as Item);
      return () => h("div", {}, [h("p", {}, 'This is a "radio" style list group. Only a single element can be selected at a time.'), h("div", {
        style: "width: 300px"
      }, [h(VItemGroup, {
        ...args,
        type: "radiogroup"
      }, {
        default: () => items.map((item, idx) => defaultItem(item, idx, selectedItem))
      })])]);
    }
  }),
  name: "Default",
  args: {
    direction: "vertical",
    bordered: true
  }
}`,...(b=(y=p.parameters)==null?void 0:y.docs)==null?void 0:b.source}}};var h,V,w;c.parameters={...c.parameters,docs:{...(h=c.parameters)==null?void 0:h.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VItemGroup,
      VItem,
      VIcon
    },
    setup() {
      const icons = ["close", "pause", "play", "replay"];
      const items = new Array(icons.length).fill(null).map((_, i) => ({
        id: i,
        label: \`Item \${i}\`,
        icon: icons[i]
      }));
      const selectedItemIds = ref(new Set<number>());
      const toggleItem = (item: Item) => {
        if (selectedItemIds.value.delete(item.id)) {
          selectedItemIds.value = new Set(selectedItemIds.value);
        } else {
          selectedItemIds.value = new Set(selectedItemIds.value.add(item.id));
        }
      };
      return () => h("div", {}, [h("p", {}, menuDescription), h("div", {
        style: "width: 300px"
      }, [h(VItemGroup, {
        ...args,
        type: "menu"
      }, {
        default: () => items.map((item, idx) => menuItem(item, idx, selectedItemIds, toggleItem))
      })])]);
    }
  }),
  name: "Menu",
  args: {
    direction: "vertical",
    bordered: true
  }
}`,...(w=(V=c.parameters)==null?void 0:V.docs)==null?void 0:w.source}}};var _,S,x;u.parameters={...u.parameters,docs:{...(_=u.parameters)==null?void 0:_.docs,source:{originalSource:`{
  render: args => ({
    components: {
      VButton,
      VPopover,
      VItem,
      VItemGroup,
      VIcon
    },
    setup() {
      const icons = ["close", "pause", "play", "replay"];
      const items = new Array(icons.length).fill(null).map((_, i) => ({
        id: i,
        label: \`Item \${i}\`,
        icon: icons[i]
      }));
      const selectedItemIds = ref(new Set<number>());
      const toggleItem = (item: Item) => {
        if (selectedItemIds.value.delete(item.id)) {
          selectedItemIds.value = new Set(selectedItemIds.value);
        } else {
          selectedItemIds.value = new Set(selectedItemIds.value.add(item.id));
        }
      };
      return () => h(VPopover, {
        id: "item-group-popover"
      }, {
        trigger: ({
          a11yProps,
          visible
        }: TriggerProps) => h(VButton, {
          variant: "filled-pink-8",
          size: "medium",
          ...a11yProps,
          pressed: visible
        }, {
          default: () => visible ? "Close menu" : "Open menu"
        }),
        default: () => [h(VItemGroup, {
          ...args,
          type: "menu"
        }, {
          default: () => items.map((item, idx) => menuItem(item, idx, selectedItemIds, toggleItem, args.direction))
        })]
      });
    }
  }),
  name: "Popover",
  args: {
    direction: "vertical",
    bordered: false
  }
}`,...(x=(S=u.parameters)==null?void 0:S.docs)==null?void 0:x.source}}};const ee=["Default","Menu","Popover"];export{p as Default,c as Menu,u as Popover,ee as __namedExportsOrder,Z as default};
