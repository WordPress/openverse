import{u as s}from"./Nz2p3Woh.js";import{u as l}from"./C1-0vP3w.js";import{V as t}from"./BnZHsc1a.js";import"./CDFarRZf.js";import{h as n}from"./Bf-AzR54.js";import"./shqyu_m_.js";import"./UQnQ_SvL.js";import"./BOvEjOPJ.js";import"./DHILWyHo.js";import"./DP0Qqza0.js";import"./B06Wl6je.js";import"./6POF_SQB.js";import"./nResBSny.js";import"./B78A4_tv.js";import"./rZ73O98I.js";import"./bYPJlIeP.js";import"./BF6vVg7M.js";import"./DzAq6MI-.js";import"./olEHfY3b.js";import"./CADoQZ_l.js";import"./nHVt-A68.js";import"./Big7CaLo.js";import"./HitohTq8.js";import"./8vSlX9Dy.js";import"./DhTbjJlp.js";import"./Bipwsjfb.js";import"./D31f7pVw.js";import"./G-2gs7Wx.js";import"./Xl6n5ahl.js";import"./B1H9ZU0Z.js";import"./D9JVarWf.js";import"./DTP0RB-8.js";import"./FADBYOvo.js";import"./BkbAmEqc.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="1693d0d1-f7a0-4dc4-b033-ca58517bfbed",e._sentryDebugIdIdentifier="sentry-dbid-1693d0d1-f7a0-4dc4-b033-ca58517bfbed")}catch{}})();const p=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],u=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:p},sourceNames:{image:u}}),s().$patch({results:{image:{count:240}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,c,m;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
