import{h as a}from"./DwwldUEF.js";import{u as s}from"./Gc5ScyLZ.js";import{u as l}from"./KlWK2kB1.js";import{V as t}from"./BtvhIGOg.js";import"./CjQ0HQF0.js";import"./C6VqcP4x.js";import"./CFZbsX2Q.js";import"./Ley1esUq.js";import"./C0pA7UPR.js";import"./rq0rg1X-.js";import"./Ck0CgHQL.js";import"./CUsfujdM.js";import"./DmsD6orq.js";import"./BIohVJVH.js";import"./BuC5_mLh.js";import"./BufT_yKp.js";import"./DcMSHMAp.js";import"./DzAq6MI-.js";import"./CD6Nr1ia.js";import"./B67cIdux.js";import"./Cqs9wCPQ.js";import"./D9b6d0V7.js";import"./Bu-vEs7l.js";import"./Dwl_h6Xz.js";import"./DhTbjJlp.js";import"./DyhVoU-3.js";import"./D7DxMZPa.js";import"./Bl4H7SX1.js";import"./DZZ1Fr_1.js";import"./C5DaQLrz.js";import"./Ct9P1Zdp.js";import"./D93TPuWH.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="fb656a6a-c7a2-4584-8060-bfe4479eb7bb",e._sentryDebugIdIdentifier="sentry-dbid-fb656a6a-c7a2-4584-8060-bfe4479eb7bb")}catch{}})();const p=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],u=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:p},sourceNames:{image:u}}),s().$patch({results:{image:{count:240}}}),()=>a("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>a(t,{...i,class:"bg-default"})))}}),name:"All collections"};var n,c,m;o.parameters={...o.parameters,docs:{...(n=o.parameters)==null?void 0:n.docs,source:{originalSource:`{
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
