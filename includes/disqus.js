var scripts = document.getElementsByTagName('script');
var dsqscript = scripts[scripts.length-1];
var disqus_shortname = dsqscript.getAttribute('data-disqus-shortname');

(function() {
	  var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
	  dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
	  (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
})();
