DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Router Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gray-900 text-white min-h-screen p-6">
    <div class="max-w-4xl mx-auto bg-gray-800 p-6 rounded-2xl shadow-xl border border-gray-700">
        
        <!-- Header -->
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-2xl font-bold text-blue-400">AI Router Console</h1>
            <button onclick="toggleProviderForm()" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-bold text-xl flex items-center gap-2">
                <i class="fa-solid fa-plus"></i> Add API Key
            </button>
        </div>

        <!-- 1. Form (Hidden by default, opens on Plus click) -->
        <div id="providerForm" class="hidden bg-gray-700 p-5 rounded-xl mb-6 border border-gray-600">
            <h2 class="text-lg font-semibold mb-3">Add & Verify Provider</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input id="name" placeholder="Provider Name (e.g. Groq, OpenAI)" class="bg-gray-800 border border-gray-600 p-2 rounded">
                <input id="api_key" type="password" placeholder="Enter Your API Key" class="bg-gray-800 border border-gray-600 p-2 rounded">
                <input id="model_name" placeholder="Enter Your Model (e.g. gpt-4o, llama-3.3-70b)" class="bg-gray-800 border border-gray-600 p-2 rounded">
                <input id="base_url" placeholder="Enter Your URL" value="https://api.openai.com/v1" class="bg-gray-800 border border-gray-600 p-2 rounded">
            </div>
            <div class="mt-4 flex items-center gap-4">
                <button onclick="verifyAndSaveProvider()" class="bg-green-600 hover:bg-green-500 text-white font-semibold px-6 py-2 rounded-lg">Done</button>
                <div id="checkResult" class="text-sm font-bold"></div>
            </div>
        </div>

        <!-- Saved API Keys List -->
        <div class="mb-8">
            <h3 class="text-md font-semibold text-gray-300 mb-2">Available API Keys</h3>
            <div id="providersList" class="flex flex-wrap gap-2 text-sm"></div>
        </div>

        <!-- 2. Select Routing Box (Low, Medium, Hard) -->
        <h2 class="text-xl font-bold mb-3 text-yellow-400">Word Limit Mapping & Routing</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            
            <!-- Low Box -->
            <div class="bg-gray-700 p-4 rounded-xl border border-gray-600 text-center">
                <h3 class="text-lg font-bold text-green-400">LOW</h3>
                <p class="text-xs text-gray-300 mb-3">20 शब्द +</p>
                <select id="low_select" class="w-full bg-gray-800 border border-gray-600 p-2 rounded text-sm"></select>
            </div>

            <!-- Medium Box -->
            <div class="bg-gray-700 p-4 rounded-xl border border-gray-600 text-center">
                <h3 class="text-lg font-bold text-yellow-400">MEDIUM</h3>
                <p class="text-xs text-gray-300 mb-3">50 शब्द +</p>
                <select id="medium_select" class="w-full bg-gray-800 border border-gray-600 p-2 rounded text-sm"></select>
            </div>

            <!-- Hard Box -->
            <div class="bg-gray-700 p-4 rounded-xl border border-gray-600 text-center">
                <h3 class="text-lg font-bold text-red-400">HARD</h3>
                <p class="text-xs text-gray-300 mb-3">100 शब्द +</p>
                <select id="hard_select" class="w-full bg-gray-800 border border-gray-600 p-2 rounded text-sm"></select>
            </div>
        </div>

        <!-- 3. Generate Production Key -->
        <div class="bg-gray-700 p-5 rounded-xl border border-gray-600">
            <h2 class="text-lg font-semibold mb-3">Generate Production Key</h2>
            <div class="flex flex-col md:flex-row gap-4 mb-4">
                <input id="company_name" placeholder="Company Name" class="bg-gray-800 border border-gray-600 p-2 rounded flex-1">
                <button onclick="generateProductionKey()" class="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded-lg font-bold">
                    Generate Production Key
                </button>
            </div>
            <div id="keyOutput" class="p-3 bg-gray-800 rounded border border-gray-600 font-mono text-green-400 break-all hidden"></div>
        </div>

    </div>

    <script>
        function toggleProviderForm() {
            document.getElementById('providerForm').classList.toggle('hidden');
        }

        async function verifyAndSaveProvider() {
            const checkResult = document.getElementById('checkResult');
            checkResult.className = "text-sm font-bold text-yellow-400";
            checkResult.innerText = "Checking credentials...";

            const data = {
                name: document.getElementById('name').value,
                api_key: document.getElementById('api_key').value,
                base_url: document.getElementById('base_url').value,
                model_name: document.getElementById('model_name').value
            };

            const res = await fetch('/admin/providers/verify-and-add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await res.json();
            if (res.ok && result.valid) {
                checkResult.className = "text-sm font-bold text-green-400 flex items-center gap-1";
                checkResult.innerHTML = '<i class="fa-solid fa-circle-check"></i> Yes (Verified & Saved)';
                loadProviders();
            } else {
                checkResult.className = "text-sm font-bold text-red-400";
                checkResult.innerText = "❌ Invalid Credentials";
            }
        }

        async function loadProviders() {
            const res = await fetch('/admin/providers');
            const data = await res.json();
            
            let listHtml = '';
            let optionsHtml = '<option value="">Select API Key</option>';

            data.forEach(p => {
                listHtml += `<span class="bg-gray-800 border border-gray-600 px-3 py-1 rounded-full text-xs text-blue-300">✔ ${p.name} (${p.model_name})</span>`;
                optionsHtml += `<option value="${p.id}">${p.name} - ${p.model_name}</option>`;
            });

            document.getElementById('providersList').innerHTML = listHtml || "<span class='text-gray-500'>No active providers</span>";
            document.getElementById('low_select').innerHTML = optionsHtml;
            document.getElementById('medium_select').innerHTML = optionsHtml;
            document.getElementById('hard_select').innerHTML = optionsHtml;
        }

        async function generateProductionKey() {
            const company = document.getElementById('company_name').value;
            const low = document.getElementById('low_select').value;
            const medium = document.getElementById('medium_select').value;
            const hard = document.getElementById('hard_select').value;

            if(!company || !low || !medium || !hard) {
                alert("कृपया कंपनी का नाम और तीनों लेवल्स के लिए API Keys चुनें!");
                return;
            }

            const data = {
                company_name: company,
                low_provider_id: parseInt(low),
                medium_provider_id: parseInt(medium),
                hard_provider_id: parseInt(hard)
            };

            const res = await fetch('/admin/product-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await res.json();
            const out = document.getElementById('keyOutput');
            out.classList.remove('hidden');
            out.innerText = "Production Key: " + result.product_key;
        }

        loadProviders();
    </script>
</body>
</html>
"""
