// The invitation is the iCloud share link in ?s=…; the app opens this page's link itself (universal link)
// when it's installed, so whoever sees this page most likely doesn't have the app yet.
const params = new URLSearchParams(location.search);
const share = params.get('s');
const open = document.getElementById('open');
if (share && /^https:\/\/www\.icloud\.com\/share\//.test(share)) {
  open.href = share;
  open.hidden = false;
}
if (!(navigator.language || 'de').toLowerCase().startsWith('de')) {
  document.documentElement.lang = 'en';
  document.title = 'Household book invitation – Finance Tracker';
  document.getElementById('title').textContent = 'Household book invitation';
  document.getElementById('text').innerHTML = 'You were invited to a shared household book in <strong>Finance Tracker</strong>. Get the app, then open this link again.';
  document.getElementById('store').textContent = 'Get Finance Tracker';
  open.textContent = 'I have the app – open invitation';
  document.getElementById('hint').textContent = 'Finance Tracker is free for iPhone and iPad. The book is shared through iCloud.';
}
// On iPhone and iPad: hand the invitation to iOS right away. With the app installed, the iCloud link
// opens Finance Tracker and joins the book; without it, Apple's iCloud page offers the App Store.
// Coming back (e.g. after installing) shows this page with both buttons instead of looping.
const isApple = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
if (isApple && !open.hidden && !sessionStorage.getItem('ft-opened')) {
  sessionStorage.setItem('ft-opened', '1');
  setTimeout(() => { location.href = share; }, 300);
}
