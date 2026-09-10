import{h as a}from"./DwwldUEF.js";import{u as s}from"./Ds_kB4O7.js";import{u as l}from"./D8qJDlnG.js";import{V as t}from"./B-gxTr-H.js";import"./CWoQmekT.js";import"./Z8zkSHZ1.js";import"./CAa63J2U.js";import"./BAdCBbtP.js";import"./Dl1S6mqo.js";import"./TLA9Fm80.js";import"./Ck0CgHQL.js";import"./aHnQ5-ra.js";import"./ghAvikQd.js";import"./Bkc2CSET.js";import"./I6oWuQE1.js";import"./VcnMPoS3.js";import"./C8BbUAkk.js";import"./DzAq6MI-.js";import"./Cyc9srVp.js";import"./DqyB4W5h.js";import"./BtS8wA1z.js";import"./tAHCZdDM.js";import"./DoSYsHAz.js";import"./aezMCrU2.js";import"./DhTbjJlp.js";import"./BUaahbsN.js";import"./CcNWDV0w.js";import"./Dhs1Or-2.js";import"./CUvT7aun.js";import"./BGi7wlVR.js";import"./CUCjtGpu.js";import"./D93TPuWH.js";import"./CU-snwr6.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="fb656a6a-c7a2-4584-8060-bfe4479eb7bb",e._sentryDebugIdIdentifier="sentry-dbid-fb656a6a-c7a2-4584-8060-bfe4479eb7bb")}catch{}})();const p=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],u=["smithsonian_african_american_history_museum","flickr","met"],R={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:p},sourceNames:{image:u}}),s().$patch({results:{image:{count:240}}}),()=>a("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>a(t,{...i,class:"bg-default"})))}}),name:"All collections"};var n,c,m;o.parameters={...o.parameters,docs:{...(n=o.parameters)==null?void 0:n.docs,source:{originalSource:`{
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
