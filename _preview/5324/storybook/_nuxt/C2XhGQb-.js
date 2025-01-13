import{u as s}from"./BKvBQNfv.js";import{u as l}from"./BXlC2Afm.js";import{V as t}from"./Cg3Yekv8.js";import"./BQ2uyTwE.js";import{h as n}from"./ueSFnAt6.js";import"./BKGw6EjD.js";import"./BUcLuzj5.js";import"./D9PGBJDx.js";import"./CxIz9G_3.js";import"./DSEYgdJX.js";import"./cS2ccka-.js";import"./EYmIadoG.js";import"./nu0uObuU.js";import"./CP2tuLu8.js";import"./5wCrcqN-.js";import"./C4YS0AQy.js";import"./C_jCWbT6.js";import"./DzAq6MI-.js";import"./DHgysDkh.js";import"./A1b6Lb8y.js";import"./BQNGXNMh.js";import"./DDGXuWLI.js";import"./CFNrPCvG.js";import"./B_AFY9SJ.js";import"./DhTbjJlp.js";import"./KoGT8mmZ.js";import"./DlgfYiH5.js";import"./DKvPnfU5.js";import"./DI2Xpw6B.js";import"./C6BGRyAK.js";import"./dNCV0R31.js";import"./CIRXjnDb.js";import"./rltOz0pP.js";import"./cXVshVQU.js";import"./DNI0JtzU.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="b1d4773c-15fc-4590-9331-1a7020123efe",e._sentryDebugIdIdentifier="sentry-dbid-b1d4773c-15fc-4590-9331-1a7020123efe")}catch{}})();const p=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],u=["smithsonian_african_american_history_museum","flickr","met"],W={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:p},sourceNames:{image:u}}),s().$patch({results:{image:{count:240}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,c,m;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
}`,...(m=(c=o.parameters)==null?void 0:c.docs)==null?void 0:m.source}}};const X=["AllCollections"];export{o as AllCollections,X as __namedExportsOrder,W as default};
