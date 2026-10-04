DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Router Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen">
    <div class="max-w-5xl mx-auto py-10 px-4">
        <h1 class="text-3xl font-bold mb-2">AI Router Dashboard</h1>
        <p class="text-gray-600 mb-8">Cost Saving Multi-Model Router</p>

        <!-- Add Provider -->
        <div class="bg-white rounded-xl shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">1. Add API Provider</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input id="name" placeholder="Name (OpenAI, Anthropic...)" class="border p-2 rounded">
                <input id="api_key" placeholder="API Key" class="border p-2 rounded">
                <input id="base_url" placeholder="Base URL" value="https://api.openai.com/v1" class="border p-2 rounded">
                <input id="model_name" placeholder="Model Name (gpt-4o-mini)" class="border p-2 rounded">
                <select id="tier" class="border p-2 rounded">
                    <option value="cheap">Cheap</option>
                    <option value="medium">Medium</option>
                    <option value="expensive">Expensive</option>
                </select>
                <button onclick="addProvider()" class="bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                    Add Provider
                </button>
            </div>
            <p id="providerMsg" class="mt-3 text-sm"></p>
        </div>

        <!-- Generate Product Key -->
        <div class="bg-white rounded-xl shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">2. Generate Product Key (Permanent)</h2>
            <div class="flex gap-4">
                <input id="company_name" placeholder="Company Name" class="border p-2 rounded flex-1">
                <button onclick="generateKey()" class="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">
                    Generate Product Key
                </button>
            </div>
            <p id="keyMsg" class="mt-3 text-sm font-mono"></p>
        </div>

        <!-- Current Providers -->
        <div class="bg-white rounded-xl shadow p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Current Providers</h2>
            <div id="providersList" class="text-sm"></div>
        </div>

        <!-- Current Product Keys -->
        <div class="bg-white rounded-xl shadow p-6">
            <h2 class="text-xl font-semibold mb-4">Active Product Keys (Always ON)</h2>
            <div id="keysList" class="text-sm"></div>
        </div>
    </div>

    <script>
        async function addProvider() {
            const data = {
                name: document.getElementById('name').value,
                api_key: document.getElementById('api_key').value,
                base_url: document.getElementById('base_url').value,
                model_name: document.getElementById('model_name').value,
                tier: document.getElementById('tier').value
            };
            const res = await fetch('/admin/providers', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            document.getElementById('providerMsg').innerText = result.message || JSON.stringify(result);
            loadProviders();
        }

        async function generateKey() {
            const data = {
                name: document.getElementById('company_name').value || "Company Product",
                company_name: document.getElementById('company_name').value
            };
            const res = await fetch('/admin/product-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            document.getElementById('keyMsg').innerText = "Product Key: " + result.product_key;
            loadKeys();
        }

        async function loadProviders() {
            const res = await fetch('/admin/providers');
            const data = await res.json();
            let html = data.map(p => 
                `<div class="border-b py-2">${p.tier.toUpperCase()} → \( {p.name} ( \){p.model_name})</div>`
            ).join('');
            document.getElementById('providersList').innerHTML = html || "No providers yet";
        }

        async function loadKeys() {
            const res = await fetch('/admin/product-keys');
            const data = await res.json();
            let html = data.map(k => 
                `<div class="border-b py-2 font-mono">${k.key} — ${k.name} ${k.is_active ? '(Active)' : '(Deleted)'}</div>`
            ).join('');
            document.getElementById('keysList').innerHTML = html || "No product keys yet";
        }

        loadProviders();
        loadKeys();
    </script>
</body>
</html>
"""