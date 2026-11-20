// Set once Levano is in the App Store (numeric ID from App Store Connect).
const APP_STORE_ID = '';

// The invite lives in the fragment (#id=…&t=…&n=…), so it never reaches the server's logs.
// With the app installed, iOS opens this link in Levano directly (universal link); this page is the fallback.
const params = new URLSearchParams(location.hash.slice(1));
const id = params.get('id') || '';
const token = params.get('t') || '';
const name = (params.get('n') || '').slice(0, 40);
const valid = /^[0-9a-f-]{36}$/i.test(id) && /^[0-9a-z]{16,128}$/i.test(token);
const english = !(navigator.language || 'de').toLowerCase().startsWith('de');

const store = document.getElementById('store');
const soon = document.getElementById('soon');
const open = document.getElementById('open');
if (APP_STORE_ID) {
  store.href = 'https://apps.apple.com/app/id' + APP_STORE_ID;
  store.hidden = false;
} else {
  soon.hidden = false;
}
if (valid) {
  open.href = 'ferrum://friend?id=' + encodeURIComponent(id) + '&t=' + encodeURIComponent(token);
  open.hidden = false;
}

if (english) {
  document.documentElement.lang = 'en';
  document.title = 'Invitation to Levano';
  document.getElementById('title').textContent = 'Train with me on Levano';
  document.getElementById('f1').textContent = 'Share your workouts and records';
  document.getElementById('f2').textContent = 'Give each other high fives and comments';
  document.getElementById('f3').textContent = 'Compare your best lifts';
  store.textContent = 'Get Levano';
  soon.textContent = 'Coming soon to the App Store';
  open.textContent = 'I have the app – open invitation';
  document.getElementById('hint').textContent = 'If you have Levano, the invitation opens right in the app. Otherwise get the app, then open this link again.';
}
// The name comes from the link and is only shown as text; the app checks the invitation with the server.
const text = document.getElementById('text');
text.textContent = '';
const strong = document.createElement('strong');
strong.textContent = 'Levano';
if (name) {
  const who = document.createElement('strong');
  who.textContent = name;
  text.append(who, english ? ' invited you to connect on ' : ' hat dich eingeladen, euch in ', strong, english ? '.' : ' zu verbinden.');
} else {
  text.append(english ? 'You were invited to connect on ' : 'Du wurdest eingeladen, dich in ', strong, english ? '.' : ' zu verbinden.');
}
