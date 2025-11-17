import{r as g,h as s}from"./DwwldUEF.js";import{_ as l,V as d,i as G}from"./DHuvU6af.js";import{V as m}from"./DoSYsHAz.js";import{_ as I}from"./DQR6Jndg.js";import{V as f}from"./Dhs1Or-2.js";import"./CWoQmekT.js";import"./CzJ3cZ9I.js";import"./DZP0BHtF.js";import"./VcnMPoS3.js";import"./cfTPNM7V.js";import"./TLA9Fm80.js";import"./DhTbjJlp.js";import"./aezMCrU2.js";import"./tAHCZdDM.js";import"./CUuqYMuc.js";import"./Ck0CgHQL.js";import"./8zTACUTo.js";import"./PhiECvvt.js";import"./CUvT7aun.js";import"./DqyB4W5h.js";import"./BtS8wA1z.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="d8979fc7-e2ba-4c82-9bed-20752f05d7c0",e._sentryDebugIdIdentifier="sentry-dbid-d8979fc7-e2ba-4c82-9bed-20752f05d7c0")}catch{}})();const Y={title:"Components/VItemGroup",component:l,subcomponents:{VItem:d,VIcon:m,VPopover:I,VButton:f},argTypes:{direction:{options:G,control:{type:"radio"}},bordered:{control:{type:"boolean"}}}},P='This is a "menu" style item group. Multiple items can be active at a time and all have the "menuitemcheckbox" role.',k=(e,r,i)=>s(d,{key:e.id,selected:i.value.id===e.id,isFirst:r===0,onClick:()=>{i.value=e},size:"medium"},{default:()=>[s(m,{name:e.icon}),s("span",{},e.label)]}),D=(e,r,i,t,a)=>s(d,{key:e.id,selected:i.value.has(e.id),isFirst:r===0,onClick:()=>t(e),size:"medium"},{default:()=>[s(m,{name:e.icon}),s("span",{class:a==="horizontal"?"pe-2":""},e.label)]}),c={render:e=>({components:{VItemGroup:l,VItem:d,VIcon:m},setup(){const r=["close","pause","play","replay"],i=new Array(r.length).fill(null).map((a,n)=>({id:n,label:`Item ${n}`,icon:r[n]})),t=g({});return()=>s("div",{},[s("p",{},'This is a "radio" style list group. Only a single element can be selected at a time.'),s("div",{style:"width: 300px"},[s(l,{...e,type:"radiogroup"},{default:()=>i.map((a,n)=>k(a,n,t))})])])}}),name:"Default",args:{direction:"vertical",bordered:!0}},p={render:e=>({components:{VItemGroup:l,VItem:d,VIcon:m},setup(){const r=["close","pause","play","replay"],i=new Array(r.length).fill(null).map((n,o)=>({id:o,label:`Item ${o}`,icon:r[o]})),t=g(new Set),a=n=>{t.value.delete(n.id)?t.value=new Set(t.value):t.value=new Set(t.value.add(n.id))};return()=>s("div",{},[s("p",{},P),s("div",{style:"width: 300px"},[s(l,{...e,type:"menu"},{default:()=>i.map((n,o)=>D(n,o,t,a))})])])}}),name:"Menu",args:{direction:"vertical",bordered:!0}},u={render:e=>({components:{VButton:f,VPopover:I,VItem:d,VItemGroup:l,VIcon:m},setup(){const r=["close","pause","play","replay"],i=new Array(r.length).fill(null).map((n,o)=>({id:o,label:`Item ${o}`,icon:r[o]})),t=g(new Set),a=n=>{t.value.delete(n.id)?t.value=new Set(t.value):t.value=new Set(t.value.add(n.id))};return()=>s(I,{id:"item-group-popover"},{trigger:({a11yProps:n,visible:o})=>s(f,{variant:"filled-pink-8",size:"medium",...n,pressed:o},{default:()=>o?"Close menu":"Open menu"}),default:()=>[s(l,{...e,type:"menu"},{default:()=>i.map((n,o)=>D(n,o,t,a,e.direction))})]})}}),name:"Popover",args:{direction:"vertical",bordered:!1}};var v,y,b;c.parameters={...c.parameters,docs:{...(v=c.parameters)==null?void 0:v.docs,source:{originalSource:`{
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
}`,...(b=(y=c.parameters)==null?void 0:y.docs)==null?void 0:b.source}}};var h,V,w;p.parameters={...p.parameters,docs:{...(h=p.parameters)==null?void 0:h.docs,source:{originalSource:`{
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
}`,...(w=(V=p.parameters)==null?void 0:V.docs)==null?void 0:w.source}}};var _,S,x;u.parameters={...u.parameters,docs:{...(_=u.parameters)==null?void 0:_.docs,source:{originalSource:`{
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
}`,...(x=(S=u.parameters)==null?void 0:S.docs)==null?void 0:x.source}}};const Z=["Default","Menu","Popover"];export{c as Default,p as Menu,u as Popover,Z as __namedExportsOrder,Y as default};
