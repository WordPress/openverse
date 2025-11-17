(function(){try{var e=typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},f=new e.Error().stack;f&&(e._sentryDebugIds=e._sentryDebugIds||{},e._sentryDebugIds[f]="0e7eff94-f2b3-43eb-85f4-a42d1e8fb852",e._sentryDebugIdIdentifier="sentry-dbid-0e7eff94-f2b3-43eb-85f4-a42d1e8fb852")}catch{}})();function b(e){for(var f=[],i=1;i<arguments.length;i++)f[i-1]=arguments[i];var n=Array.from(typeof e=="string"?[e]:e);n[n.length-1]=n[n.length-1].replace(/\r?\n([\t ]*)$/,"");var g=n.reduce(function(t,s){var d=s.match(/\n([\t ]+|(?!\s).)/g);return d?t.concat(d.map(function(u){var r,a;return(a=(r=u.match(/[\t ]/g))===null||r===void 0?void 0:r.length)!==null&&a!==void 0?a:0})):t},[]);if(g.length){var c=new RegExp(`
[	 ]{`+Math.min.apply(Math,g)+"}","g");n=n.map(function(t){return t.replace(c,`
`)})}n[0]=n[0].replace(/^\r?\n/,"");var o=n[0];return f.forEach(function(t,s){var d=o.match(/(?:^|\n)( *)$/),u=d?d[1]:"",r=t;typeof t=="string"&&t.includes(`
`)&&(r=String(t).split(`
`).map(function(a,l){return l===0?a:""+u+a}).join(`
`)),o+=r+n[s+1]}),o}export{b as d};
