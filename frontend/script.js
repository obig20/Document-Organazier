const API_BASE = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:8000'
  : '';

async function postJson(path, payload) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  return res.json();
}

async function getJson(path) {
  const res = await fetch(`${API_BASE}${path}`);
  return res.json();
}

function setJson(id, data) {
  document.getElementById(id).textContent = JSON.stringify(data, null, 2);
}

document.getElementById('classifyBtn').addEventListener('click', async () => {
  const text = document.getElementById('inputText').value;
  const lang = document.getElementById('lang').value;
  const top_k = parseInt(document.getElementById('topk').value, 10) || 3;
  const data = await postJson('/api/classify', { text, lang, top_k });
  setJson('classifyResult', data);
});

document.getElementById('trainBtn').addEventListener('click', async () => {
  const lang = document.getElementById('train-lang').value;
  const category = document.getElementById('category').value.trim();
  const keywordsRaw = document.getElementById('keywords').value;
  const keywords = keywordsRaw.split(',').map(k => k.trim()).filter(Boolean);
  const data = await postJson('/api/train', { lang, category, keywords });
  setJson('trainResult', data);
});

document.getElementById('clusterBtn').addEventListener('click', async () => {
  const lines = document.getElementById('clusterTexts').value.split('\n').map(l => l.trim()).filter(Boolean);
  const num_clusters = parseInt(document.getElementById('clusters').value, 10) || 3;
  const data = await postJson('/api/cluster', { texts: lines, num_clusters });
  setJson('clusterResult', data);
});

document.getElementById('rulesBtn').addEventListener('click', async () => {
  const data = await getJson('/api/rules');
  setJson('rulesResult', data);
});