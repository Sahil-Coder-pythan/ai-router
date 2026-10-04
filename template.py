DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Router Console & History</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .dropdown:hover .dropdown-menu { display: block; }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen p-6 relative">

    <div class="max-w-4xl mx-auto bg-gray-800 p-6 rounded-2xl shadow-xl border border-gray-700">
        
        <!-- Header with Top Right 3-Dots Menu -->
        <div class="flex justify-between items-center mb-6 border-b border-gray-700 pb-4">
            <h1 class="text-2xl font-bold text-blue-400">AI Router Console</h1>
            <div class="flex items-center gap-4">
                <button onclick="toggleProviderForm()" class="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg font-bold text-sm flex items-center gap-2">
                    <i class="fa-solid fa-plus"></i> Add Provider Key
                </button>
                <button onclick="openCompanyHistory()" class="text-gray-300 hover:text-white text-2xl p-2 rounded-lg hover:bg-gray-700 transition" title="Saved History">
                    <i class="fa-solid fa-ellipsis-vertical"></i>
                </button>
            </div>
        </div>

        <!-- 1. Add Provider Form -->
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
            <h3 class="text-md font-semibold text-gray-300 mb-2">Available Active API Keys</h3>
            <div id="providersList" class="flex flex-wrap gap-2 text-sm"></div>
        </div>

        <!-- 2. Routing Box -->
        <h2 class="text-xl font-bold mb-3 text-yellow-400">Word Limit Mapping & Routing</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div class="bg-gray-700 p-4 rounded-xl border border-gray-600 text-center">
                <h3 class="text-lg font-bold text-green-400">LOW</h3>
                <p class="text-xs text-gray-300 mb-3">Chote Sawal (20 Words+)</p>
                <select id="low_select" class="w-full bg-gray-800 border border-gray-600 p-2 rounded text-sm"></select>
            </div>
            <div class="bg-gray-700 p-4 rounded-xl border border-gray-600 text-center">
                <h3 class="text-lg font-bold text-yellow-400">MEDIUM</h3>
                <p class="text-xs text-gray-300 mb-3">Medium Sawal (50 Words+)</p>
                <select id="medium_select" class="w-full bg-gray-800 border border-gray-600 p-2 rounded text-sm"></select>
            </div>
            <div class="bg-gray-700 p-4 rounded-xl border border-gray-600 text-center">
                <h3 class="text-lg font-bold text-red-400">HARD</h3>
                <p class="text-xs text-gray-300 mb-3">Coding / Detailed (100 Words+)</p>
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
            
            <div id="keyOutputCard" class="hidden p-4 bg-gray-800 rounded-lg border border-gray-600 flex justify-between items-center">
                <div>
                    <span class="text-xs text-green-400 font-bold block mb-1">✔ Safe & Permanent in Database</span>
                    <span id="keyOutput" class="font-mono text-green-400 text-sm break-all"></span>
                </div>
            </div>
        </div>

    </div>

    <!-- Right Side Isolated History Drawer -->
    <div id="historyDrawer" class="fixed right-0 top-0 h-full w-96 bg-gray-800 border-l border-gray-700 shadow-2xl p-5 transform translate-x-full transition-transform duration-300 z-50 overflow-y-auto">
        <div class="flex justify-between items-center mb-6 border-b border-gray-700 pb-3">
            <h3 class="text-lg font-bold text-blue-400"><i class="fa-solid fa-lock"></i> Isolated History</h3>
            <button onclick="toggleHistoryDrawer()" class="text-gray-400 hover:text-white text-xl">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>

        <div id="historyList" class="space-y-4">
            <p class="text-gray-400 text-sm">Loading company history...</p>
        </div>
    </div>

    <script>
        function toggleProviderForm() {
            document.getElementById('providerForm').classList.toggle('hidden');
        }

        function toggleHistoryDrawer() {
            const drawer = document.getElementById('historyDrawer');
            drawer.classList.toggle('translate-x-full');
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
                checkResult.innerHTML = '<i class="fa-solid fa-circle-check"></i> Verified & Saved';
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
            const company = document.getElementById('company_name').value.trim();
            const low = document.getElementById('low_select').value;
            const medium = document.getElementById('medium_select').value;
            const hard = document.getElementById('hard_select').value;

            if(!company || !low || !medium || !hard) {
                alert("Kripya Company Name aur teeno levels ke liye API Keys chunein!");
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
            document.getElementById('keyOutputCard').classList.remove('hidden');
            document.getElementById('keyOutput').innerText = result.product_key;
            alert("Production key generated & saved in DB!");
        }

        async function openCompanyHistory() {
            const company = document.getElementById('company_name').value.trim();
            if(!company) {
                alert("Kripya pehle Company Name field mein apna naam daalein!");
                return;
            }

            toggleHistoryDrawer();
            fetchHistory(company);
        }

        async function fetchHistory(companyName) {
            const listContainer = document.getElementById('historyList');
            listContainer.innerHTML = '<p class="text-gray-400 text-sm">History load ho rahi hai...</p>';

            const res = await fetch(`/admin/history/${encodeURIComponent(companyName)}`);
            if(!res.ok) {
                listContainer.innerHTML = '<p class="text-red-400 text-sm">History fetch nahi ho saki.</p>';
                return;
            }

            const data = await res.json();
            if(!data.history || data.history.length === 0) {
                listContainer.innerHTML = `<p class="text-gray-400 text-sm">"<b>${companyName}</b>" ki koi history nahi mili.</p>`;
                return;
            }

            let html = "";
            data.history.forEach(item => {
                html += `
                    <div class="bg-gray-900 border border-gray-700 p-3 rounded-lg flex justify-between items-start">
                        <div>
                            <span class="text-xs font-bold text-purple-400 block">${item.company_name}</span>
                            <span class="font-mono text-xs text-green-400 break-all">${item.key}</span>
                        </div>
                        <button onclick="deleteKeyFromDB(${item.id}, '${companyName}')" class="text-gray-400 hover:text-red-400 text-sm ml-2" title="Delete Key">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </div>
                `;
            });
            listContainer.innerHTML = html;
        }

        async function deleteKeyFromDB(keyId, companyName) {
            if(!confirm("Kya aap sach mein is key ko permanent delete karna chahte hain?")) return;

            const res = await fetch(`/admin/history/delete/${keyId}`, { method: 'DELETE' });
            if(res.ok) {
                alert("Key database se delete ho gayi!");
                fetchHistory(companyName);
            } else {
                alert("Key delete nahi ho saki!");
            }
        }

        loadProviders();
    </script>
</body>
</html>
"""
