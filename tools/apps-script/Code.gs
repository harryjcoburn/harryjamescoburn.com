/**
 * Scorecard report sender for harryjamescoburn.com
 *
 * The scorecard page posts the raw answers here. This script:
 *   1. rebuilds the score and report from its own copy of the questions
 *      (so nobody can make it send text they wrote),
 *   2. passes the lead to HubSpot (form "Scorecard report request"),
 *   3. emails the report from Gmail as harry@harryjamescoburn.com,
 *      which is signed for the domain, so it lands in the inbox.
 *
 * Deploy: Deploy > New deployment > Web app, execute as me, access: anyone.
 * Run testSend() once from the editor to authorise and send a test to NOTIFY.
 */

var CFG = {
  FROM: 'harry@harryjamescoburn.com',
  NAME: 'Harry James Coburn',
  NOTIFY: 'harry@hcoburn.com',
  BOOK: 'https://cal.com/harryjamescoburn/intro?utm_source=scorecard&utm_medium=email',
  SITE: 'https://harryjamescoburn.com',
  HS_URL: 'https://api-eu1.hsforms.com/submissions/v3/integration/submit/149589438/e6a11b52-1579-41a2-a7f8-4ce15ad47af6',
  HS_SUB: 3921244406,
  DAILY_MAX: 80,           // safety cap on reports per day
  PER_ADDRESS_HOURS: 6     // one report per address per 6 hours
};

var AREAS = [
  {k:'strategy', n:'Strategy', lever:'Win rate, deal size',
   m:'Pull your last 20 wins and losses, write down what the best fits share, and make one pitch in their words. Price on the value they get, and start saying no.'},
  {k:'win', n:'Win', lever:'Time to close, win rate',
   m:'Write exit criteria for every stage and find the one stage where most deals stall. Fix that first.'},
  {k:'grow', n:'Grow', lever:'Net retention',
   m:'Agree a first-impact goal with every new customer in their first 30 days, and give one person ownership of renewals and expansion.'},
  {k:'team', n:'Team', lever:'Deals created, win rate',
   m:'Map every handover from first touch to onboarding, and give new hires a written 30-60-90.'},
  {k:'motivation', n:'Motivation', lever:'Deals created, deal size',
   m:'Rebuild targets from capacity and conversion, and pay for good-fit revenue and price held, not just volume.'},
  {k:'rhythm', n:'Rhythm', lever:'Time to close, and every other lever',
   m:'Run one 45-minute weekly review on the five levers: the stuck deals, the next step on each, and one experiment.'},
  {k:'systems', n:'Systems', lever:'Every lever',
   m:'Make only the fields that matter mandatory, build one dashboard everyone trusts, then add agents trained on your data and checked against your standard.'}
];
var STAGES = ['Seed', 'Series A', 'Series B', 'Series C+'];
var FOCUS = {launch:'Launching a new market or product', stall:'Growth has stalled since the raise',
             founder:'Sales still runs through the founder', ai:'Making AI actually work in sales'};
var EXTRA = {launch:'For a new market or product, we\'d prove the formula small before scaling it.',
             stall:'After a raise, the fastest wins are usually in strategy and the Win stations.',
             founder:'Getting sales out of the founder\'s head starts with the pitch and the handovers.',
             ai:'AI works when it\'s trained on your data and checked against your standard. That\'s where I\'d focus.'};

function doGet() {
  return json_({ok: true, service: 'scorecard-report'});
}

function doPost(e) {
  var d;
  try { d = JSON.parse(e.postData.contents); } catch (err) { return json_({ok: false, error: 'bad_json'}); }
  if (d.website) return json_({ok: true});              // honeypot: bots fill hidden fields
  if (d.type === 'resource') return resource_(d);
  if (d.type === 'message') return message_(d);
  if (d.type === 'agent') return agent_(d, (e.parameter || {}).k);
  var lead = clean_(d);
  if (lead.error) return json_({ok: false, error: lead.error});

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var cache = CacheService.getScriptCache();
    var key = 'sent_' + Utilities.base64EncodeWebSafe(lead.email);
    if (cache.get(key)) return json_({ok: true, repeat: true});
    var props = PropertiesService.getScriptProperties();
    var day = Utilities.formatDate(new Date(), 'Europe/Berlin', 'yyyy-MM-dd');
    var count = props.getProperty('day') === day ? +props.getProperty('count') : 0;
    if (count >= CFG.DAILY_MAX) { notify_('Scorecard daily cap reached', lead); return json_({ok: false, error: 'busy'}); }
    props.setProperties({day: day, count: String(count + 1)});
    cache.put(key, '1', CFG.PER_ADDRESS_HOURS * 3600);
  } finally { lock.releaseLock(); }

  var r = report_(lead);
  var hs = toHubSpot_(lead, r);
  var sent = false, err = '';
  try { sendReport_(lead, r); sent = true; } catch (x) { err = String(x); }
  if (!sent || !hs.ok) notify_('Scorecard report problem', lead, 'email sent: ' + sent + ' ' + err + '\nHubSpot: ' + hs.code + ' ' + hs.body);
  return json_({ok: sent, hubspot: hs.ok});
}

function clean_(d) {
  function txt(v, max) {
    v = String(v || '').replace(/[\r\n\t<>]/g, ' ').replace(/\s+/g, ' ').trim();
    if (/https?:|www\.|\.[a-z]{2,}\//i.test(v)) v = '';  // no links in names
    return v.slice(0, max);
  }
  var email = String(d.email || '').trim().toLowerCase();
  if (!/^[^@\s<>]+@[^@\s<>]+\.[a-z]{2,}$/i.test(email) || email.length > 120) return {error: 'email'};
  var first = txt(d.firstname, 40);
  if (!first) return {error: 'name'};
  if (d.consent !== true) return {error: 'consent'};
  var answers = {};
  for (var i = 0; i < AREAS.length; i++) {
    var v = +(d.answers || {})[AREAS[i].k];
    if ([1, 2, 3, 5].indexOf(v) < 0) return {error: 'answers'};
    answers[AREAS[i].k] = v;
  }
  if (STAGES.indexOf(d.stage) < 0 || !FOCUS[d.sit]) return {error: 'answers'};
  return {email: email, firstname: first, company: txt(d.company, 80), stage: d.stage, sit: d.sit,
          answers: answers, source: txt(d.source, 120) || 'direct', page: txt(d.page, 200)};
}

function report_(lead) {
  var scores = AREAS.map(function (a) { return {a: a, s: lead.answers[a.k]}; });
  var avg = scores.reduce(function (t, x) { return t + x.s; }, 0) / scores.length;
  var band, text;
  if (avg < 2.2) { band = 'Running on heroics'; text = 'Revenue depends on a few people working very hard. The good news: the first fixes are usually fast and visible.'; }
  else if (avg < 3.7) { band = 'Works, but depends on people'; text = 'The engine runs, but it leaks and it won\'t scale on its own. This is where the biggest gains usually are.'; }
  else { band = 'Ready to scale'; text = 'The basics are in place. The question now is how far AI and new markets can take it.'; }
  var rec;
  if (avg < 2.6) rec = 'a GTM Diagnostic. We\'d stop the bleeding in your weakest layers within 30 days, then plan the engine.';
  else if (avg < 3.7) rec = 'a GTM Diagnostic, then a Commercial Systems Build for the layers holding you back.';
  else rec = 'a GTM Teardown to find the next level, or an advisory role while you scale.';
  var sorted = scores.slice().sort(function (x, y) { return x.s - y.s; });
  return {score: avg.toFixed(1), band: band, text: text, rec: rec, extra: EXTRA[lead.sit],
          scores: scores, moves: sorted.slice(0, 3), focus: FOCUS[lead.sit]};
}

function sendReport_(lead, r) {
  var subject = 'Your sales engine scorecard: ' + r.score + ' out of 5';
  var plain = 'Hi ' + lead.firstname + ',\n\n' +
    'Thanks for taking the scorecard. Here is your report.\n\n' +
    'YOUR SCORE: ' + r.score + ' out of 5 (' + r.band + ')\n' + r.text + '\n\n' +
    'YOUR THREE FIRST MOVES\n' + r.moves.map(function (x, i) { return (i + 1) + '. ' + x.a.n + ': ' + x.a.m; }).join('\n') + '\n\n' +
    'ALL SEVEN LAYERS\n' + r.scores.map(function (x) { return x.a.n + ': ' + (x.s === 2 ? 'not sure' : x.s + '/5'); }).join('\n') + '\n\n' +
    'Where I\'d start: ' + r.rec + ' ' + r.extra + '\n\n' +
    'If you want to talk it through, book 30 minutes here: ' + CFG.BOOK + '\n' +
    'Or just reply to this email. I read every one.\n\n' +
    'Thanks,\nHarry\n\n' +
    '--\nHarry James Coburn, Charlottenburger Straße 136B, 13086 Berlin, Germany\n' + CFG.SITE + '\n' +
    'You asked for this report on ' + CFG.SITE + '/scorecard.html. Reply "unsubscribe" and I won\'t email you again.';

  var C = {ink: '#16181d', soft: '#5b606b', line: '#e4e2dc', accent: '#b4532a', bg: '#faf9f6'};
  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  var bars = r.scores.map(function (x) {
    var w = Math.round(x.s / 5 * 100);
    return '<tr><td style="padding:6px 12px 6px 0;font-size:14px;color:' + C.ink + ';white-space:nowrap">' + esc(x.a.n) + '</td>' +
      '<td style="padding:6px 0;width:100%"><div style="background:' + C.line + ';height:8px;border-radius:4px"><div style="background:' + (x.s <= 2 ? C.accent : C.ink) + ';width:' + w + '%;height:8px;border-radius:4px"></div></div></td>' +
      '<td style="padding:6px 0 6px 12px;font-size:14px;color:' + C.soft + ';text-align:right">' + (x.s === 2 ? '?' : x.s) + '</td></tr>';
  }).join('');
  var moves = r.moves.map(function (x, i) {
    return '<tr><td style="padding:12px 0;border-top:1px solid ' + C.line + '"><div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:' + C.soft + '">' + (i + 1) + ' · ' + esc(x.a.lever) + '</div>' +
      '<div style="font-size:16px;font-weight:600;margin:4px 0;color:' + C.ink + '">' + esc(x.a.n) + '</div>' +
      '<div style="font-size:15px;line-height:1.5;color:' + C.ink + '">' + esc(x.a.m) + '</div></td></tr>';
  }).join('');
  var html = '<!doctype html><html><body style="margin:0;background:' + C.bg + ';font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:' + C.ink + '">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:' + C.bg + '"><tr><td align="center" style="padding:24px 16px">' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:580px;background:#fff;border:1px solid ' + C.line + ';border-radius:8px"><tr><td style="padding:28px">' +
    '<p style="font-size:16px;line-height:1.5;margin:0 0 16px">Hi ' + esc(lead.firstname) + ',</p>' +
    '<p style="font-size:16px;line-height:1.5;margin:0 0 24px">Thanks for taking the scorecard. Here is your report.</p>' +
    '<div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:' + C.soft + '">Your score</div>' +
    '<div style="font-size:40px;font-weight:700;line-height:1.1;margin:4px 0">' + r.score + '<span style="font-size:16px;font-weight:400;color:' + C.soft + '"> out of 5</span></div>' +
    '<div style="font-size:18px;font-weight:600;margin:8px 0 4px">' + esc(r.band) + '</div>' +
    '<p style="font-size:15px;line-height:1.5;margin:0 0 24px;color:' + C.soft + '">' + esc(r.text) + '</p>' +
    '<div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:' + C.soft + ';margin-bottom:4px">Your three first moves</div>' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0">' + moves + '</table>' +
    '<div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:' + C.soft + ';margin:24px 0 8px">All seven layers</div>' +
    '<table role="presentation" width="100%" cellpadding="0" cellspacing="0">' + bars + '</table>' +
    '<p style="font-size:15px;line-height:1.5;margin:24px 0 0"><b>Where I\'d start:</b> ' + esc(r.rec) + ' ' + esc(r.extra) + '</p>' +
    '<p style="margin:24px 0"><a href="' + CFG.BOOK + '" style="display:inline-block;background:' + C.ink + ';color:#fff;text-decoration:none;padding:12px 20px;border-radius:6px;font-size:15px">Book 30 minutes with me</a></p>' +
    '<p style="font-size:15px;line-height:1.5;margin:0 0 16px">Or just reply to this email. I read every one.</p>' +
    '<p style="font-size:15px;line-height:1.5;margin:0">Thanks,<br>Harry</p>' +
    '</td></tr></table>' +
    '<p style="max-width:580px;font-size:12px;line-height:1.5;color:' + C.soft + ';margin:16px auto 0">Harry James Coburn · Charlottenburger Straße 136B, 13086 Berlin, Germany · <a href="' + CFG.SITE + '" style="color:' + C.soft + '">harryjamescoburn.com</a><br>' +
    'You asked for this report on harryjamescoburn.com. Reply "unsubscribe" and I won\'t email you again.</p>' +
    '</td></tr></table></body></html>';

  var opts = {htmlBody: html, name: CFG.NAME, replyTo: CFG.FROM, bcc: CFG.NOTIFY};
  if (GmailApp.getAliases().indexOf(CFG.FROM) >= 0 || Session.getActiveUser().getEmail() === CFG.FROM) opts.from = CFG.FROM;
  GmailApp.sendEmail(lead.email, subject, plain, opts);
}

function toHubSpot_(lead, r) {
  var report = 'YOUR THREE FIRST MOVES\n' + r.moves.map(function (x, i) { return (i + 1) + '. ' + x.a.n + ': ' + x.a.m; }).join('\n') +
    '\n\nALL SEVEN LAYERS\n' + r.scores.map(function (x) { return x.a.n + ': ' + (x.s === 2 ? 'not sure' : x.s + '/5'); }).join('\n') +
    '\n\nWhere I\'d start: ' + r.rec + ' ' + r.extra;
  var fields = [['firstname', lead.firstname], ['email', lead.email], ['company', lead.company],
    ['scorecard_score', r.score], ['scorecard_band', r.band], ['scorecard_stage', lead.stage],
    ['scorecard_focus', r.focus], ['scorecard_report', report], ['scorecard_source', lead.source]];
  var body = {
    fields: fields.map(function (f) { return {objectTypeId: '0-1', name: f[0], value: String(f[1])}; }),
    context: {pageUri: lead.page || CFG.SITE + '/scorecard.html', pageName: 'Sales engine scorecard'},
    legalConsentOptions: {consent: {consentToProcess: true,
      text: 'I agree to Harry James Coburn storing my details to send the report.',
      communications: [{value: true, subscriptionTypeId: CFG.HS_SUB,
        text: 'Send me the report and an occasional follow-up from Harry. Unsubscribe any time.'}]}}
  };
  try {
    var res = UrlFetchApp.fetch(CFG.HS_URL, {method: 'post', contentType: 'application/json',
      payload: JSON.stringify(body), muteHttpExceptions: true});
    var code = res.getResponseCode();
    return {ok: code >= 200 && code < 300, code: code, body: res.getContentText().slice(0, 500)};
  } catch (x) { return {ok: false, code: 0, body: String(x)}; }
}

function notify_(subject, lead, extra) {
  try { MailApp.sendEmail(CFG.NOTIFY, subject, (extra || '') + '\n\n' + JSON.stringify(lead, null, 2)); } catch (x) {}
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Run once from the editor: authorises the script and sends a sample report to NOTIFY. */
function testSend() {
  var lead = clean_({firstname: 'Harry', email: CFG.NOTIFY, company: 'Test', stage: 'Series A', sit: 'stall', consent: true,
    answers: {strategy: 3, win: 1, grow: 2, team: 3, motivation: 1, rhythm: 3, systems: 5}, source: 'apps-script test'});
  var r = report_(lead);
  sendReport_(lead, r);
  Logger.log('Aliases: ' + GmailApp.getAliases().join(', '));
  Logger.log('Sent test report to ' + CFG.NOTIFY);
}

/* ---------- Free resources (PDF packs) ---------- */
var RESOURCES = {
  prompts:   {title: 'The Sales Agent Prompt Pack', file: 'hjc-sales-agent-prompts-7k2q.pdf',
              blurb: 'Seven production prompts, one for each layer of the engine, with how to check each one.'},
  workflows: {title: 'Sales Agent Workflows', file: 'hjc-agent-workflows-p9x4.pdf',
              blurb: 'Three end-to-end builds, step by step: the inbound agent, the outbound signal engine and a lead engine on free tools.'},
  skills:    {title: 'Claude Skills for Sales', file: 'hjc-claude-skills-for-sales-m3v8.pdf',
              blurb: 'Five ready-to-use skills with the full SKILL.md files and templates for your reference files.'}
};

function resource_(d) {
  var res = RESOURCES[d.resource];
  if (!res) return json_({ok: false, error: 'resource'});
  var email = String(d.email || '').trim().toLowerCase();
  if (!/^[^@\s<>]+@[^@\s<>]+\.[a-z]{2,}$/i.test(email) || email.length > 120) return json_({ok: false, error: 'email'});
  var first = String(d.firstname || '').replace(/[\r\n\t<>]/g, ' ').replace(/\s+/g, ' ').trim();
  if (/https?:|www\.|\.[a-z]{2,}\//i.test(first)) first = '';
  first = first.slice(0, 40);
  if (!first) return json_({ok: false, error: 'name'});
  if (d.consent !== true) return json_({ok: false, error: 'consent'});
  var url = CFG.SITE + '/assets/downloads/packs/' + res.file;

  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    var cache = CacheService.getScriptCache();
    var key = 'res_' + d.resource + '_' + Utilities.base64EncodeWebSafe(email);
    if (cache.get(key)) return json_({ok: true, repeat: true, url: url});
    var props = PropertiesService.getScriptProperties();
    var day = Utilities.formatDate(new Date(), 'Europe/Berlin', 'yyyy-MM-dd');
    var count = props.getProperty('day') === day ? +props.getProperty('count') : 0;
    if (count >= CFG.DAILY_MAX) return json_({ok: false, error: 'busy'});
    props.setProperties({day: day, count: String(count + 1)});
    cache.put(key, '1', CFG.PER_ADDRESS_HOURS * 3600);
  } finally { lock.releaseLock(); }

  var src = String(d.source || 'direct').replace(/[\r\n<>]/g, ' ').slice(0, 120);
  var hs = {ok: false, code: 0, body: ''};
  try {
    var r = UrlFetchApp.fetch(CFG.HS_URL, {method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      payload: JSON.stringify({
        fields: [{objectTypeId: '0-1', name: 'firstname', value: first}, {objectTypeId: '0-1', name: 'email', value: email},
                 {objectTypeId: '0-1', name: 'resource_requested', value: res.title + ' (' + src + ')'}],
        context: {pageUri: String(d.page || CFG.SITE + '/ai.html').slice(0, 200), pageName: 'AI in sales'},
        legalConsentOptions: {consent: {consentToProcess: true,
          text: 'I agree to Harry James Coburn storing my details to send the resource.',
          communications: [{value: true, subscriptionTypeId: CFG.HS_SUB,
            text: 'Send me the resource and an occasional follow-up from Harry. Unsubscribe any time.'}]}}})});
    hs = {ok: r.getResponseCode() < 300, code: r.getResponseCode(), body: r.getContentText().slice(0, 300)};
  } catch (x) { hs.body = String(x); }

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  var subject = res.title + ': your copy';
  var plain = 'Hi ' + first + ',\n\nHere is your copy of ' + res.title + ':\n' + url + '\n\n' + res.blurb + '\n\n' +
    'They are starting points. Test them on your own data before you trust them, and hold them to the 95% rule: only let an agent run on its own once your best person would send 95% of what it writes.\n\n' +
    'If you want to talk about building any of this into your sales engine, book 30 minutes: ' + CFG.BOOK + '\nOr just reply. I read every one.\n\nThanks,\nHarry\n\n' +
    '--\nHarry James Coburn, Charlottenburger Straße 136B, 13086 Berlin, Germany\n' + CFG.SITE + '\nYou asked for this on ' + CFG.SITE + '. Reply "unsubscribe" and I won\'t email you again.';
  var html = '<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;font-size:15px;line-height:1.55;color:#16181d;max-width:560px">' +
    '<p>Hi ' + esc(first) + ',</p><p>Here is your copy of <b>' + esc(res.title) + '</b>. ' + esc(res.blurb) + '</p>' +
    '<p style="margin:22px 0"><a href="' + url + '" style="display:inline-block;background:#10372A;color:#fff;text-decoration:none;padding:12px 20px;border-radius:6px">Download the PDF</a></p>' +
    '<p>They are starting points. Test them on your own data before you trust them, and hold them to the 95% rule: only let an agent run on its own once your best person would send 95% of what it writes.</p>' +
    '<p>If you want to talk about building any of this into your sales engine, <a href="' + CFG.BOOK + '">book 30 minutes</a>, or just reply. I read every one.</p>' +
    '<p>Thanks,<br>Harry</p>' +
    '<p style="font-size:12px;color:#5b606b;margin-top:28px">Harry James Coburn · Charlottenburger Straße 136B, 13086 Berlin, Germany · <a href="' + CFG.SITE + '" style="color:#5b606b">harryjamescoburn.com</a><br>You asked for this on harryjamescoburn.com. Reply "unsubscribe" and I won\'t email you again.</p></div>';
  var sent = false, err = '';
  try {
    var opts = {htmlBody: html, name: CFG.NAME, replyTo: CFG.FROM, bcc: CFG.NOTIFY};
    if (GmailApp.getAliases().indexOf(CFG.FROM) >= 0) opts.from = CFG.FROM;
    GmailApp.sendEmail(email, subject, plain, opts); sent = true;
  } catch (x) { err = String(x); }
  if (!sent || !hs.ok) notify_('Resource request problem', {email: email, resource: d.resource}, 'email sent: ' + sent + ' ' + err + '\nHubSpot: ' + hs.code + ' ' + hs.body);
  return json_({ok: sent, hubspot: hs.ok, url: url});
}

/* ---------- Contact form messages ---------- */
function message_(d) {
  var email = String(d.email || '').trim().toLowerCase();
  if (!/^[^@\s<>]+@[^@\s<>]+\.[a-z]{2,}$/i.test(email) || email.length > 120) return json_({ok: false, error: 'email'});
  function line(v, max) { return String(v || '').replace(/[\r\n\t<>]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max); }
  var first = line(d.firstname, 40), company = line(d.company, 80);
  var msg = String(d.message || '').replace(/\r/g, '').trim().slice(0, 2000);
  if (!first) return json_({ok: false, error: 'name'});
  if (msg.length < 5) return json_({ok: false, error: 'message'});
  if (d.consent !== true) return json_({ok: false, error: 'consent'});

  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    var cache = CacheService.getScriptCache(), key = 'msg_' + Utilities.base64EncodeWebSafe(email);
    var n = +(cache.get(key) || 0);
    if (n >= 3) return json_({ok: true, repeat: true});            // max 3 messages per address per hour
    cache.put(key, String(n + 1), 3600);
    var props = PropertiesService.getScriptProperties();
    var day = Utilities.formatDate(new Date(), 'Europe/Berlin', 'yyyy-MM-dd');
    var count = props.getProperty('day') === day ? +props.getProperty('count') : 0;
    if (count >= CFG.DAILY_MAX) return json_({ok: false, error: 'busy'});
    props.setProperties({day: day, count: String(count + 1)});
  } finally { lock.releaseLock(); }

  var src = line(d.source, 120) || 'direct';
  var hs = {ok: false, code: 0, body: ''};
  try {
    var r = UrlFetchApp.fetch(CFG.HS_URL, {method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      payload: JSON.stringify({
        fields: [['firstname', first], ['email', email], ['company', company], ['message', msg]].map(function (f) { return {objectTypeId: '0-1', name: f[0], value: f[1]}; }),
        context: {pageUri: line(d.page, 200) || CFG.SITE + '/contact.html', pageName: 'Send a message'},
        legalConsentOptions: {consent: {consentToProcess: true, text: 'I agree to Harry James Coburn storing my details to reply to my message.', communications: []}}})});
    hs = {ok: r.getResponseCode() < 300, code: r.getResponseCode(), body: r.getContentText().slice(0, 300)};
  } catch (x) { hs.body = String(x); }

  // Only Harry receives this email, so the visitor's text never goes to anyone else.
  var body = 'New message from harryjamescoburn.com\n\nFrom: ' + first + (company ? ' (' + company + ')' : '') + ' <' + email + '>\n' +
    'Source: ' + src + '\nHubSpot: ' + (hs.ok ? 'saved' : 'NOT saved (' + hs.code + ')') + '\n\n' + msg + '\n\nReply to this email to answer them directly.';
  var sent = false;
  try { GmailApp.sendEmail(CFG.NOTIFY, 'Website message from ' + first + (company ? ', ' + company : ''), body, {name: 'harryjamescoburn.com', replyTo: email}); sent = true; } catch (x) {}
  return json_({ok: sent || hs.ok, hubspot: hs.ok});
}

/* ---------- Website voice agent (ElevenLabs webhook tool) ---------- */
// The key is a shared secret: the ElevenLabs tool sends it as ?k=..., so only Harry's agent can post here.
var AGENT_KEY = 'SET_IN_EDITOR';  // the real key lives only in the Apps Script editor

function agent_(d, key) {
  if (key !== AGENT_KEY) return json_({ok: false, error: 'forbidden'});
  function line(v, max) { return String(v || '').replace(/[\r\n\t<>]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max); }
  var name = line(d.visitor_name, 60), company = line(d.company, 80), next = line(d.next_step, 200);
  var email = String(d.visitor_email || '').trim().toLowerCase();
  if (!/^[^@\s<>]+@[^@\s<>]+\.[a-z]{2,}$/i.test(email) || email.length > 120) email = '';
  var summary = String(d.summary || '').replace(/\r/g, '').trim().slice(0, 3000);
  if (!summary) return json_({ok: false, error: 'summary'});
  var consent = d.consent_to_contact === true || d.consent_to_contact === 'true';

  var props = PropertiesService.getScriptProperties();
  var day = Utilities.formatDate(new Date(), 'Europe/Berlin', 'yyyy-MM-dd');
  var count = props.getProperty('day') === day ? +props.getProperty('count') : 0;
  if (count >= CFG.DAILY_MAX) return json_({ok: false, error: 'busy'});
  props.setProperties({day: day, count: String(count + 1)});

  var hs = {ok: false, code: 0};
  if (email && consent) {
    try {
      var r = UrlFetchApp.fetch(CFG.HS_URL, {method: 'post', contentType: 'application/json', muteHttpExceptions: true,
        payload: JSON.stringify({
          fields: [['firstname', name.split(' ')[0] || ''], ['email', email], ['company', company], ['message', 'Website voice agent: ' + summary.slice(0, 1500)]]
            .map(function (f) { return {objectTypeId: '0-1', name: f[0], value: f[1]}; }),
          context: {pageUri: CFG.SITE + '/ai.html', pageName: 'Voice agent'},
          legalConsentOptions: {consent: {consentToProcess: true, text: 'Agreed in the voice conversation that Harry James Coburn may store these details to follow up.', communications: []}}})});
      hs = {ok: r.getResponseCode() < 300, code: r.getResponseCode()};
    } catch (x) {}
  }
  var body = 'Conversation with your website voice agent\n\n' +
    'Visitor: ' + (name || 'not given') + (company ? ' (' + company + ')' : '') + '\n' +
    'Email: ' + (email || 'not given') + (email ? (consent ? ' (agreed to follow-up)' : ' (no consent to follow up)') : '') + '\n' +
    'HubSpot: ' + (email && consent ? (hs.ok ? 'saved' : 'NOT saved (' + hs.code + ')') : 'not saved') + '\n' +
    'Suggested next step: ' + (next || 'none') + '\n\n' + summary + '\n\nFull transcript: ElevenLabs > Agents > Ask Harry\'s AI > Conversations.';
  var opts = {name: 'harryjamescoburn.com'};
  if (email && consent) opts.replyTo = email;
  try { GmailApp.sendEmail(CFG.NOTIFY, 'Voice agent: ' + (name || 'website visitor') + (company ? ', ' + company : ''), body, opts); } catch (x) {}
  return json_({ok: true});
}
