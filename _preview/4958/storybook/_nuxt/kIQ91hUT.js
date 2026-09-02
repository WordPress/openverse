import{u as m}from"./nLTbcOiO.js";import{u as c}from"./QKPGpISV.js";import{V as e}from"./C9RLDPcl.js";import{h as r}from"./lKNUlTH_.js";import"./xwskLidM.js";import"./DivIZ7Lb.js";import"./C0voMBC3.js";import"./CFMQYC2y.js";import"./Dt-H8hG_.js";import"./CTON8dBl.js";import"./CzMkt2mC.js";import"./Cpj98o6Y.js";import"./Ci7G4jyV.js";import"./Xs_VBmP5.js";import"./CeIx8O89.js";import"./BR9eDTPM.js";import"./CVtkxrq9.js";import"./D0ww02ZN.js";import"./CA4HNXs5.js";import"./CIg47mny.js";import"./MXhTc5uu.js";import"./CuPsdpTl.js";import"./DlAUqK2U.js";import"./D3k3o1NF.js";import"./CTONR9_B.js";import"./9Q23NzEb.js";import"./BOX21o1p.js";import"./c1er4GOR.js";import"./2vq21tXV.js";import"./BSEdKPgk.js";import"./C67TMzvP.js";import"./5ehHOY6F.js";const s=[{source_name:"smithsonian_african_american_history_museum",display_name:"Smithsonian Institution: National Museum of African American History and Culture",source_url:"https://nmaahc.si.edu",logo_url:null,media_count:10895},{source_name:"flickr",display_name:"Flickr",source_url:"https://www.flickr.com",logo_url:null,media_count:505849755},{source_name:"met",display_name:"Metropolitan Museum of Art",source_url:"https://www.metmuseum.org",logo_url:null,media_count:396650}],l=["smithsonian_african_american_history_museum","flickr","met"],K={title:"Components/VCollectionHeader",component:e},p=[{collectionName:"tag",collectionParams:{collection:"tag",tag:"cat"},mediaType:"image"},{collectionName:"source",collectionParams:{collection:"source",source:"met"},mediaType:"image"},{collectionName:"creator",collectionParams:{collection:"creator",source:"flickr",creator:"iocyoungreporters"},mediaType:"image",creatorUrl:"https://www.flickr.com/photos/126018610@N05"},{collectionName:"source-with-long-name",collectionParams:{collection:"source",source:"smithsonian_african_american_history_museum"},mediaType:"image"}],o={render:()=>({components:{VCollectionHeader:e},setup(){return c().$patch({providers:{image:s},sourceNames:{image:l}}),m().$patch({results:{image:{count:240}}}),()=>r("div",{class:"wrapper w-full p-3 flex flex-col gap-4 bg-surface"},p.map(n=>r(e,{...n,class:"bg-default"})))}}),name:"All collections"};var t,i,a;o.parameters={...o.parameters,docs:{...(t=o.parameters)==null?void 0:t.docs,source:{originalSource:`{
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
}`,...(a=(i=o.parameters)==null?void 0:i.docs)==null?void 0:a.source}}};const L=["AllCollections"];export{o as AllCollections,L as __namedExportsOrder,K as default};
