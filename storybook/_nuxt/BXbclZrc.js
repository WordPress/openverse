import{h as n}from"./53SD24Bo.js";import{u as m}from"./DD0JbomO.js";import{u as l}from"./CdxtYFZI.js";import{V as t}from"./H6XThqf4.js";import"./_bbq3c9C.js";import"./DZOi7sP9.js";import"./DDS--uLL.js";import"./DGyM8Eie.js";import"./DVthAQU8.js";import"./B9k6C3Hw.js";import"./7RO02bE1.js";import"./8DNOLO2n.js";import"./C1DVfU3S.js";import"./iProge2w.js";import"./Dm0sd39P.js";import"./B_-6Taiq.js";import"./CUnsfT8r.js";import"./okj3qyDJ.js";import"./Cy_NKsXi.js";import"./BOewZ2sR.js";import"./D2GrBf-6.js";import"./DjsporFN.js";import"./CH5-dTGy.js";import"./dvXbmdTd.js";import"./ivjvpZKc.js";import"./DhTbjJlp.js";import"./CjHk_BZn.js";import"./IVMwpLdb.js";import"./DlboKt2a.js";import"./Di7dAt70.js";import"./CKgIdhzd.js";import"./xQ8_qGND.js";import"./B9Cuo1Ro.js";import"./BQrorSEU.js";import"./B06vE1PI.js";import"../sb-preview/runtime.js";(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},r=new e.Error().stack;r&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[r]="5c6b8f3a-e78c-4e29-9646-a546066dd607",e._sentryDebugIdIdentifier="sentry-dbid-5c6b8f3a-e78c-4e29-9646-a546066dd607")}catch{}})();const u=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],p=["smithsonian_african_american_history_museum","flickr","met"],W={title:"Components/VCollectionHeader",component:t},d=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:t},setup(){return l().$patch({providers:{image:u},sourceNames:{image:p}}),m().$patch({results:{image:{count:240}},mediaFetchState:{image:{status:"success",error:null},audio:{status:"success",error:null}}}),()=>n("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},d.map(i=>n(t,{...i,class:"bg-default"})))}}),name:"All collections"};var a,s,c;o.parameters={...o.parameters,docs:{...(a=o.parameters)==null?void 0:a.docs,source:{originalSource:`{
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
        },
        mediaFetchState: {
          image: {
            status: "success",
            error: null
          },
          audio: {
            status: "success",
            error: null
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
}`,...(c=(s=o.parameters)==null?void 0:s.docs)==null?void 0:c.source}}};const X=["AllCollections"];export{o as AllCollections,X as __namedExportsOrder,W as default};
