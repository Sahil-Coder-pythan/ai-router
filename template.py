# ==============================================================================
# ENTERPRISE DASHBOARD UI TEMPLATE WITH SPLASH SCREEN
# ==============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stratissoft - AI Router Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #0b0f17;
            color: #e2e8f0;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        /* Splash Screen Overlay */
        #splash-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: #ffffff;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: opacity 0.6s ease, visibility 0.6s ease;
        }

        .splash-logo {
            width: 90px;
            height: 90px;
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            border-radius: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 20px 30px -10px rgba(37, 99, 235, 0.4);
            animation: pulse-ring 1.8s infinite ease-in-out;
        }

        @keyframes pulse-ring {
            0% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.5);
            }
            70% {
                transform: scale(1);
                box-shadow: 0 0 0 20px rgba(37, 99, 235, 0);
            }
            100% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(37, 99, 235, 0);
            }
        }

        .splash-hidden {
            opacity: 0;
            visibility: hidden;
        }

        .glass-panel {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .glow-effect {
            box-shadow: 0 0 25px -5px rgba(59, 130, 246, 0.3);
        }
        .dropdown-menu {
            display: none;
        }
        .dropdown-menu.active {
            display: block;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col justify-between">

    <!-- LinkedIn Style Professional Splash Screen -->
    <div id="splash-screen">
        <div class="splash-logo mb-6">
            <i class="fa-solid fa-network-wired text-4xl text-white"></i>
        </div>
        <h1 class="text-3xl font-extrabold text-gray-900 tracking-wider">Stratissoft</h1>
        <p class="text-xs font-semibold text-gray-500 uppercase tracking-widest mt-2">Enterprise AI Router Engine</p>
    </div>

    <!-- Top Navigation Bar -->
    <header class="glass-panel sticky top-0 z-50 px-6 py-4 border-b border-gray-800">
        <div class="max-w-7xl mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="bg-blue-600 p-2 rounded-lg text-white">
                    <i class="fa-solid fa-network-wired text-xl"></i>
                </div>
                <div>
                    <h1 class="font-bold text-lg text-white tracking-wide">Stratissoft AI Router</h1>
                    <span class="text-xs text-green-400 font-mono flex items-center gap-1">
                        <span class="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span> Multi-Tenant Active
                    </span>
                </div>
            </div>
            
            <div class="flex items-center space-x-4">
                <div class="bg-gray-800 px-3 py-1.5 rounded-full text-xs font-mono text-gray-300 border border-gray-700">
                    <i class="fa-solid fa-server text-blue-400 mr-1.5"></i> Status: Healthy
                </div>
                <div class="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center font-bold text-sm text-white">
                    S
                </div>
            </div>
        </div>
    </header>

    <!-- Main Dashboard Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex-grow w-full">
        
        <!-- Live Analytics Quick Overview Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="glass-panel p-5 rounded-xl">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-gray-400 uppercase tracking-wider">Total Requests</p>
                        <h3 class="text-2xl font-bold text-white mt-1" id="total-requests">0</h3>
                    </div>
                    <div class="p-2 bg-blue-500/10 text-blue-400 rounded-lg"><i class="fa-solid fa-chart-line"></i></div>
                </div>
            </div>
            <div class="glass-panel p-5 rounded-xl">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-gray-400 uppercase tracking-wider">Active Keys</p>
                        <h3 class="text-2xl font-bold text-white mt-1" id="active-keys-count">0</h3>
                    </div>
                    <div class="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg"><i class="fa-solid fa-key"></i></div>
                </div>
            </div>
            <div class="glass-panel p-5 rounded-xl">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-gray-400 uppercase tracking-wider">Router Latency</p>
                        <h3 class="text-2xl font-bold text-white mt-1">~12ms</h3>
                    </div>
                    <div class="p-2 bg-purple-500/10 text-purple-400 rounded-lg"><i class="fa-solid fa-bolt"></i></div>
                </div>
            </div>
            <div class="glass-panel p-5 rounded-xl">
                <div class="flex justify-between items-start">
                    <div>
                        <p class="text-xs font-medium text-gray-400 uppercase tracking-wider">Cost Savings</p>
                        <h3 class="text-2xl font-bold text-emerald-400 mt-1">~65%</h3>
                    </div>
                    <div class="p-2 bg-amber-500/10 text-amber-400 rounded-lg"><i class="fa-solid fa-piggy-bank"></i></div>
                </div>
            </div>
        </div>

        <!-- System Credentials Setup Panel -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            
            <!-- Left Side: Add Credentials Form -->
            <div class="glass-panel p-6 rounded-2xl border border-gray-800">
                <h2 class="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <i class="fa-solid fa-plus-circle text-blue-500"></i> Add Provider Key
                </h2>
                
                <form id="add-provider-form" onsubmit="event.preventDefault(); submitCredentials();" class="space-y-4">
                    <div>
                        <label class="block text-xs font-medium text-gray-400 mb-1">Base URL</label>
                        <input type="text" id="base_url" placeholder="https://generativelanguage.googleapis.com/v1beta/openai" 
                            class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-medium text-gray-400 mb-1">Model Name</label>
                        <input type="text" id="model_name" placeholder="gemini-1.5-flash" 
                            class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>

                    <div>
                        <label class="block text-xs font-medium text-gray-400 mb-1">API Key</label>
                        <input type="password" id="api_key" placeholder="AIzaSy..." 
                            class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500">
                    </div>

                    <button type="submit" id="submit-btn" 
                        class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium py-2.5 rounded-lg text-sm transition duration-200 glow-effect flex items-center justify-center gap-2">
                        <span>Verify & Add Provider</span>
                    </button>
                </form>
                <div id="status-message" class="mt-3 text-xs text-center hidden"></div>
            </div>

            <!-- Right Side: Production Keys List & History -->
            <div class="glass-panel p-6 rounded-2xl border border-gray-800 lg:col-span-2">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-lg font-semibold text-white flex items-center gap-2">
                        <i class="fa-solid fa-list-check text-indigo-400"></i> Active Production Keys
                    </h2>
                    <span class="text-xs text-gray-400">Enterprise Access Isolated</span>
                </div>

                <!-- Production Keys Table / List -->
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-sm text-gray-400">
                        <thead class="bg-gray-900/50 text-xs text-gray-400 uppercase font-mono border-b border-gray-800">
                            <tr>
                                <th class="px-4 py-3">Model</th>
                                <th class="px-4 py-3">Base Endpoint</th>
                                <th class="px-4 py-3">Status</th>
                                <th class="px-4 py-3 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody id="keys-list-body" class="divide-y divide-gray-800">
                            <tr>
                                <td colspan="4" class="px-4 py-6 text-center text-gray-500 italic">
                                    No active keys verified yet. Add one from the form.
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="glass-panel border-t border-gray-800 py-4 px-6 text-center text-xs text-gray-500">
        Stratissoft Enterprise Gateway Router Engine &copy; 2026. All Rights Reserved.
    </footer>

    <!-- Splash Screen & Dropdown Menu Script -->
    <script>
        // Splash Screen Timer Logic
        window.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                const splash = document.getElementById('splash-screen');
                if (splash) {
                    splash.classList.add('splash-hidden');
                }
            }, 1800);
        });

        function toggleActionMenu(id) {
            const menu = document.getElementById(`action-menu-${id}`);
            document.querySelectorAll('.dropdown-menu').forEach(m => {
                if(m !== menu) m.classList.remove('active');
            });
            if(menu) menu.classList.toggle('active');
        }

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.action-btn')) {
                document.querySelectorAll('.dropdown-menu').forEach(m => m.classList.remove('active'));
            }
        });
    </script>
</body>
</html>
"""
