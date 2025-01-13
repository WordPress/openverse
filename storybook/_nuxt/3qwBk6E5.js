import{h as a}from"./DwwldUEF.js";import{u as s}from"./DyntKXIc.js";import{u as l}from"./DIa_evZO.js";import{V as t}from"./Bb0HXgcp.js";import"./BKd6qjwJ.js";import"./B_JavP0r.js";import"./DyjmqLvs.js";import"./TJSYFxys.js";import"./DXt3Hw-9.js";import"./DrQM85Nc.js";import"./Ck0CgHQL.js";import"./DeIUwsAH.js";import"./Bc_6hboB.js";import"./BJKkpTjt.js";import"./BA2RD0IG.js";import"./DEzOOYTC.js";import"./BwtrEtqR.js";import"./DzAq6MI-.js";import"./D5nIdk7e.js";import"./B7G-YaxP.js";import"./Efi66Qad.js";import"./DjJGxhuO.js";import"./D318SDY2.js";import"./BMyQprRt.js";import"./DhTbjJlp.js";import"./DVxzvkhI.js";import"./maH52C8u.js";import"./R_--_Flr.js";import"./Duzn9Bak.js";import"./BBKfqOvt.js";import"./DJYCrh4A.js";import"./D93TPuWH.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="fb656a6a-c7a2-4584-8060-bfe4479eb7bb",e._sentryDebugIdIdentifier="sentry-dbid-fb656a6a-c7a2-4584-8060-bfe4479eb7bb")}catch{}})();const p=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],u=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:p},sourceNames:{image:u}}),s().$patch({results:{image:{count:240}}}),()=>a("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>a(t,{...i,class:"bg-default"})))}}),name:"All collections"};var n,c,m;o.parameters={...o.parameters,docs:{...(n=o.parameters)==null?void 0:n.docs,source:{originalSource:`{
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
