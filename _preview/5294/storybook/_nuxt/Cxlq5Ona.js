import{u as s}from"./DmC3CRu-.js";import{u as l}from"./DUj0lNLx.js";import{V as t}from"./CpGwX1v-.js";import"./DzKe1FZy.js";import{h as n}from"./Bf-AzR54.js";import"./DypQgoql.js";import"./BKlnuUDG.js";import"./B5T0JkOB.js";import"./meB9zTZj.js";import"./RE842jSx.js";import"./B06Wl6je.js";import"./BqixEy0E.js";import"./CbeNxiKf.js";import"./C1x2Pz8-.js";import"./P6N_4fLa.js";import"./Imyqroa4.js";import"./DEFsxmui.js";import"./DzAq6MI-.js";import"./uHJqFrjm.js";import"./Mi53UD0-.js";import"./BdGbGJtZ.js";import"./KaIp0RKv.js";import"./sL22Kbl4.js";import"./CYExI-7Z.js";import"./DhTbjJlp.js";import"./DLf-S-5N.js";import"./3CPSD_Fl.js";import"./2X7CKgv5.js";import"./DJpKulq8.js";import"./Dp3KuYUR.js";import"./D9JVarWf.js";import"./CAl9Yp-W.js";import"./FADBYOvo.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="1693d0d1-f7a0-4dc4-b033-ca58517bfbed",e._sentryDebugIdIdentifier="sentry-dbid-1693d0d1-f7a0-4dc4-b033-ca58517bfbed")}catch{}})();const p=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],u=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:p},sourceNames:{image:u}}),s().$patch({results:{image:{count:240}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,c,m;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
  render: () => ({
    components: {
      VCollectionHeader
    },
    setup() {
      const providerStore = useProviderStore();
      providerStore.$patch({
        providers: {
          image: imageProviders
        },
        sourceNames: {
          image: imageProviderNames
        }
      });
      const mediaStore = useMediaStore();
      mediaStore.$patch({
        results: {
          image: {
            count: 240
          }
        }
      });
      return () => h("div", {
        class: "wrapper w-full p-3 flex flex-col gap-4 bg-surface"
      }, collections.map(collection => h(VCollectionHeader, {
        ...(collection as typeof VCollectionHeader.props),
        class: "bg-default"
      })));
    }
  }),
  name: "All collections"
}`,...(m=(c=o.parameters)==null?void 0:c.docs)==null?void 0:m.source}}};const W=["AllCollections"];export{o as AllCollections,W as __namedExportsOrder,R as default};
