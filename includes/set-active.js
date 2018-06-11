if (document.location.href.match("/about")) {
  document.getElementById('link-blog').className = "nav-link nav-text";
  document.getElementById('link-about').className = "active nav-link nav-text";
} else {
  document.getElementById('link-blog').className = "active nav-link nav-text";
  document.getElementById('link-about').className = "nav-link nav-text";
}
