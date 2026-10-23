import{d as H}from"./CCDnPiep.js";(function(){try{var r=typeof E<"u"?E:typeof I<"u"?I:typeof self<"u"?self:{},e=new r.Error().stack;e&&(r._sentryDebugIds=r._sentryDebugIds||{},r._sentryDebugIds[e]="6077f460-c25f-4178-9c6f-cb04069e79e8",r._sentryDebugIdIdentifier="sentry-dbid-6077f460-c25f-4178-9c6f-cb04069e79e8")}catch{}})();const{useEffect:A,useMemo:h}=__STORYBOOK_MODULE_PREVIEW_API__,{global:I}=__STORYBOOK_MODULE_GLOBAL__,{logger:K}=__STORYBOOK_MODULE_CLIENT_LOGGER__;var p="backgrounds",C={light:{name:"light",value:"#F8F8F8"},dark:{name:"dark",value:"#333"}},{document:b,window:E}=I,D=()=>{var r;return!!((r=E==null?void 0:E.matchMedia("(prefers-reduced-motion: reduce)"))!=null&&r.matches)},B=r=>{(Array.isArray(r)?r:[r]).forEach(P)},P=r=>{var d;let e=b.getElementById(r);e&&((d=e.parentElement)==null||d.removeChild(e))},z=(r,e)=>{let d=b.getElementById(r);if(d)d.innerHTML!==e&&(d.innerHTML=e);else{let t=b.createElement("style");t.setAttribute("id",r),t.innerHTML=e,b.head.appendChild(t)}},U=(r,e,d)=>{var a;let t=b.getElementById(r);if(t)t.innerHTML!==e&&(t.innerHTML=e);else{let n=b.createElement("style");n.setAttribute("id",r),n.innerHTML=e;let i=`addon-backgrounds-grid${d?`-docs-${d}`:""}`,o=b.getElementById(i);o?(a=o.parentElement)==null||a.insertBefore(n,o):b.head.appendChild(n)}},j={cellSize:100,cellAmount:10,opacity:.8},G="addon-backgrounds",R="addon-backgrounds-grid",X=D()?"":"transition: background-color 0.3s;",N=(r,e)=>{let{globals:d,parameters:t,viewMode:a,id:n}=e,{options:i=C,disable:o,grid:s=j}=t[p]||{},c=d[p]||{},u=c.value,l=u?i[u]:void 0,$=(l==null?void 0:l.value)||"transparent",m=c.grid||!1,y=!!l&&!o,f=a==="docs"?`#anchor--${n} .docs-story`:".sb-show-main",_=a==="docs"?`#anchor--${n} .docs-story`:".sb-show-main",F=t.layout===void 0||t.layout==="padded",L=a==="docs"?20:F?16:0,{cellAmount:k,cellSize:g,opacity:x,offsetX:v=L,offsetY:S=L}=s,M=a==="docs"?`${G}-docs-${n}`:`${G}-color`,w=a==="docs"?n:null;A(()=>{let T=`
    ${f} {
      background: ${$} !important;
      ${X}
      }`;if(!y){B(M);return}U(M,T,w)},[f,M,w,y,$]);let O=a==="docs"?`${R}-docs-${n}`:`${R}`;return A(()=>{if(!m){B(O);return}let T=[`${g*k}px ${g*k}px`,`${g*k}px ${g*k}px`,`${g}px ${g}px`,`${g}px ${g}px`].join(", "),Y=`
        ${_} {
          background-size: ${T} !important;
          background-position: ${v}px ${S}px, ${v}px ${S}px, ${v}px ${S}px, ${v}px ${S}px !important;
          background-blend-mode: difference !important;
          background-image: linear-gradient(rgba(130, 130, 130, ${x}) 1px, transparent 1px),
           linear-gradient(90deg, rgba(130, 130, 130, ${x}) 1px, transparent 1px),
           linear-gradient(rgba(130, 130, 130, ${x/2}) 1px, transparent 1px),
           linear-gradient(90deg, rgba(130, 130, 130, ${x/2}) 1px, transparent 1px) !important;
        }
      `;z(O,Y)},[k,g,_,O,m,v,S,x]),r()},W=(r,e=[],d)=>{if(r==="transparent")return"transparent";if(e.find(a=>a.value===r)||r)return r;let t=e.find(a=>a.name===d);if(t)return t.value;if(d){let a=e.map(n=>n.name).join(", ");K.warn(H`
        Backgrounds Addon: could not find the default color "${d}".
        These are the available colors for your story based on your configuration:
        ${a}.
      `)}return"transparent"},q=(r,e)=>{var u;let{globals:d,parameters:t}=e,a=(u=d[p])==null?void 0:u.value,n=t[p],i=h(()=>n.disable?"transparent":W(a,n.values,n.default),[n,a]),o=h(()=>i&&i!=="transparent",[i]),s=e.viewMode==="docs"?`#anchor--${e.id} .docs-story`:".sb-show-main",c=h(()=>`
      ${s} {
        background: ${i} !important;
        ${D()?"":"transition: background-color 0.3s;"}
      }
    `,[i,s]);return A(()=>{let l=e.viewMode==="docs"?`addon-backgrounds-docs-${e.id}`:"addon-backgrounds-color";if(!o){B(l);return}U(l,c,e.viewMode==="docs"?e.id:null)},[o,c,e]),r()},J=(r,e)=>{var y;let{globals:d,parameters:t}=e,a=t[p].grid,n=((y=d[p])==null?void 0:y.grid)===!0&&a.disable!==!0,{cellAmount:i,cellSize:o,opacity:s}=a,c=e.viewMode==="docs",u=t.layout===void 0||t.layout==="padded"?16:0,l=a.offsetX??(c?20:u),$=a.offsetY??(c?20:u),m=h(()=>{let f=e.viewMode==="docs"?`#anchor--${e.id} .docs-story`:".sb-show-main",_=[`${o*i}px ${o*i}px`,`${o*i}px ${o*i}px`,`${o}px ${o}px`,`${o}px ${o}px`].join(", ");return`
      ${f} {
        background-size: ${_} !important;
        background-position: ${l}px ${$}px, ${l}px ${$}px, ${l}px ${$}px, ${l}px ${$}px !important;
        background-blend-mode: difference !important;
        background-image: linear-gradient(rgba(130, 130, 130, ${s}) 1px, transparent 1px),
         linear-gradient(90deg, rgba(130, 130, 130, ${s}) 1px, transparent 1px),
         linear-gradient(rgba(130, 130, 130, ${s/2}) 1px, transparent 1px),
         linear-gradient(90deg, rgba(130, 130, 130, ${s/2}) 1px, transparent 1px) !important;
      }
    `},[o]);return A(()=>{let f=e.viewMode==="docs"?`addon-backgrounds-grid-docs-${e.id}`:"addon-backgrounds-grid";if(!n){B(f);return}z(f,m)},[n,m,e]),r()},V=FEATURES!=null&&FEATURES.backgroundsStoryGlobals?[N]:[J,q],ee={[p]:{grid:{cellSize:20,opacity:.5,cellAmount:5},disable:!1,...!(FEATURES!=null&&FEATURES.backgroundsStoryGlobals)&&{values:Object.values(C)}}},Q={[p]:{value:void 0,grid:!1}},re=FEATURES!=null&&FEATURES.backgroundsStoryGlobals?Q:{[p]:null};export{V as decorators,re as initialGlobals,ee as parameters};
