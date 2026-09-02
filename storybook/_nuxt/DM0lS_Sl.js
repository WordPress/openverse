(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},d=new e.Error().stack;d&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[d]="b7dc62f4-8385-4710-9058-2fd7d0a7f79f",e._sentryDebugIdIdentifier="sentry-dbid-b7dc62f4-8385-4710-9058-2fd7d0a7f79f")}catch{}})();function h(e){for(var d=[],f=1;f<arguments.length;f++)d[f-1]=arguments[f];var n=Array.from(typeof e=="string"?[e]:e);n[n.length-1]=n[n.length-1].replace(/\r?\n([\t ]*)$/,"");var c=n.reduce(function(t,o){var i=o.match(/\n([\t ]+|(?!\s).)/g);return i?t.concat(i.map(function(s){var r,a;return(a=(r=s.match(/[\t ]/g))===null||r===void 0?void 0:r.length)!==null&&a!==void 0?a:0})):t},[]);if(c.length){var g=new RegExp(`
[	 ]{`+Math.min.apply(Math,c)+"}","g");n=n.map(function(t){return t.replace(g,`
`)})}n[0]=n[0].replace(/^\r?\n/,"");var u=n[0];return d.forEach(function(t,o){var i=u.match(/(?:^|\n)( *)$/),s=i?i[1]:"",r=t;typeof t=="string"&&t.includes(`
`)&&(r=String(t).split(`
`).map(function(a,l){return l===0?a:""+s+a}).join(`
`)),u+=r+n[o+1]}),u}export{h as d};
