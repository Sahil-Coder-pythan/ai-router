DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>AI Router Dashboard | Stratic Soft</title>

    <script src="https://cdn.tailwindcss.com"></script>

    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">

    <style>

        /* =========================================================
           STRATIC SOFT — PREMIUM ENTERPRISE UI
           Design only. Existing functionality preserved.
        ========================================================= */

        * {
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
        }

        body {
            margin: 0;
            font-family:
                Inter,
                ui-sans-serif,
                system-ui,
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            background:
                radial-gradient(circle at 15% 10%, rgba(37, 99, 235, 0.14), transparent 28%),
                radial-gradient(circle at 85% 15%, rgba(124, 58, 237, 0.12), transparent 28%),
                radial-gradient(circle at 50% 100%, rgba(14, 165, 233, 0.08), transparent 32%),
                #f4f7fb;

            color: #172033;
            min-height: 100vh;
        }

        /* =========================================================
           OPENING SCREEN
        ========================================================= */

        #openingScreen {
            position: fixed;
            inset: 0;
            z-index: 99999;

            display: flex;
            align-items: center;
            justify-content: center;

            background:
                radial-gradient(circle at center, rgba(37, 99, 235, 0.18), transparent 32%),
                linear-gradient(135deg, #07111f, #0b1728 50%, #101b31);

            transition:
                opacity 0.8s ease,
                visibility 0.8s ease;
        }

        #openingScreen.hide {
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
        }

        .opening-content {
            text-align: center;
            animation: openingEnter 1s ease forwards;
        }

        .opening-logo {
            width: 92px;
            height: 92px;

            margin: 0 auto 22px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 26px;

            color: white;
            font-size: 42px;
            font-weight: 900;

            background:
                linear-gradient(135deg, #2563eb, #4f46e5 55%, #7c3aed);

            box-shadow:
                0 0 0 1px rgba(255,255,255,0.12),
                0 20px 60px rgba(37,99,235,0.40);

            animation: logoPulse 2.2s ease-in-out infinite;
        }

        .opening-title {
            color: white;
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.8px;
        }

        .opening-subtitle {
            margin-top: 7px;
            color: #94a3b8;
            font-size: 13px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .opening-line {
            width: 150px;
            height: 3px;

            margin: 25px auto 0;

            border-radius: 999px;

            background: linear-gradient(
                90deg,
                transparent,
                #3b82f6,
                #8b5cf6,
                transparent
            );

            animation: lineMove 1.6s ease-in-out infinite;
        }

        @keyframes openingEnter {
            from {
                opacity: 0;
                transform: translateY(25px) scale(0.96);
            }

            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes logoPulse {
            0%, 100% {
                transform: scale(1);
                box-shadow:
                    0 0 0 1px rgba(255,255,255,0.12),
                    0 20px 60px rgba(37,99,235,0.35);
            }

            50% {
                transform: scale(1.045);
                box-shadow:
                    0 0 0 1px rgba(255,255,255,0.15),
                    0 24px 80px rgba(79,70,229,0.48);
            }
        }

        @keyframes lineMove {
            0%, 100% {
                opacity: 0.35;
                transform: scaleX(0.75);
            }

            50% {
                opacity: 1;
                transform: scaleX(1);
            }
        }

        /* =========================================================
           MAIN APPLICATION
        ========================================================= */

        .app-shell {
            width: 100%;
            max-width: 1180px;
            margin: 0 auto;
            padding: 26px 18px 55px;
        }

        .main-panel {
            position: relative;
            overflow: hidden;

            background: rgba(255,255,255,0.92);

            border: 1px solid rgba(148,163,184,0.22);

            border-radius: 28px;

            box-shadow:
                0 25px 70px rgba(15,23,42,0.10),
                0 4px 14px rgba(15,23,42,0.05);

            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }

        .main-panel::before {
            content: "";
            position: absolute;

            width: 420px;
            height: 420px;

            right: -220px;
            top: -220px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(59,130,246,0.09),
                    transparent 70%
                );

            pointer-events: none;
        }

        .main-panel::after {
            content: "";
            position: absolute;

            width: 320px;
            height: 320px;

            left: -180px;
            bottom: -180px;

            border-radius: 50%;

            background:
                radial-gradient(
                    circle,
                    rgba(124,58,237,0.07),
                    transparent 70%
                );

            pointer-events: none;
        }

        .content-layer {
            position: relative;
            z-index: 2;
        }

        /* =========================================================
           TOP HEADER
        ========================================================= */

        .top-header {
            overflow: visible;
            padding: 28px 30px 24px;

            display: flex;
            align-items: center;
            justify-content: space-between;

            gap: 20px;

            border-bottom: 1px solid #e8edf5;
        }

        .brand-area {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .brand-logo {
            width: 52px;
            height: 52px;

            flex-shrink: 0;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 15px;

            color: white;
            font-size: 22px;
            font-weight: 900;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #4f46e5 55%,
                    #7c3aed
                );

            box-shadow:
                0 10px 25px rgba(37,99,235,0.22);
        }

        .brand-text h1 {
            margin: 0;

            color: #111827;

            font-size: 22px;
            line-height: 1.2;
            font-weight: 800;

            letter-spacing: -0.5px;
        }

        .brand-text p {
            margin: 5px 0 0;

            color: #64748b;

            font-size: 12px;
            font-weight: 600;

            letter-spacing: 0.8px;
        }

        .header-badge {
            display: inline-flex;
            align-items: center;
            gap: 7px;

            padding: 8px 12px;

            border-radius: 999px;

            background: #f0f7ff;
            border: 1px solid #dbeafe;

            color: #2563eb;

            font-size: 11px;
            font-weight: 800;
        }

        .status-dot {
            width: 7px;
            height: 7px;

            border-radius: 50%;

            background: #22c55e;

            box-shadow: 0 0 0 4px rgba(34,197,94,0.10);
        }

        /* =========================================================
           ADD API BUTTON
        ========================================================= */

        .add-api-btn {
            border: none;
            cursor: pointer;

            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 9px;

            padding: 12px 18px;

            border-radius: 13px;

            color: white;

            font-size: 13px;
            font-weight: 800;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #4f46e5
                );

            box-shadow:
                0 10px 25px rgba(37,99,235,0.20);

            transition:
                transform 0.2s ease,
                box-shadow 0.2s ease,
                filter 0.2s ease;
        }

        .add-api-btn:hover {
            transform: translateY(-2px);

            filter: brightness(1.04);

            box-shadow:
                0 14px 30px rgba(37,99,235,0.28);
        }

        .add-api-btn:active {
            transform: translateY(0);
        }

        /* =========================================================
           SECTION
        ========================================================= */

        .section {
            padding: 25px 30px;
        }

        .section-title {
            display: flex;
            align-items: center;
            gap: 10px;

            margin-bottom: 15px;
        }

        .section-title-icon {
            width: 34px;
            height: 34px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 10px;

            color: #2563eb;

            background: #eff6ff;
            border: 1px solid #dbeafe;

            font-size: 14px;
        }

        .section-title h2,
        .section-title h3 {
            margin: 0;

            color: #172033;

            font-size: 15px;
            font-weight: 800;
        }

        .section-description {
            margin: -7px 0 18px 44px;

            color: #718096;

            font-size: 12px;
        }

        /* =========================================================
           PROVIDER FORM
        ========================================================= */

        #providerForm {
            margin: 0 30px 25px;
            padding: 23px;

            border-radius: 20px;

            background:
                linear-gradient(
                    145deg,
                    #f8fbff,
                    #f4f7ff
                );

            border: 1px solid #dce7f7;

            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.9),
                0 12px 30px rgba(15,23,42,0.05);
        }

        .form-heading {
            display: flex;
            align-items: center;
            gap: 10px;

            margin-bottom: 18px;
        }

        .form-heading i {
            color: #2563eb;
        }

        .form-heading h2 {
            margin: 0;

            color: #172033;

            font-size: 15px;
            font-weight: 800;
        }

        .premium-input {
            width: 100%;

            min-height: 45px;

            padding: 0 14px;

            border-radius: 11px;

            outline: none;

            color: #172033;

            background: white;

            border: 1px solid #dbe3ee;

            font-size: 13px;

            box-shadow:
                0 2px 7px rgba(15,23,42,0.025);

            transition:
                border-color 0.2s ease,
                box-shadow 0.2s ease,
                transform 0.2s ease;
        }

        .premium-input::placeholder {
            color: #94a3b8;
        }

        .premium-input:focus {
            border-color: #60a5fa;

            box-shadow:
                0 0 0 4px rgba(59,130,246,0.10);

            transform: translateY(-1px);
        }

        .done-btn {
            border: none;
            cursor: pointer;

            padding: 11px 20px;

            border-radius: 11px;

            color: white;

            background:
                linear-gradient(
                    135deg,
                    #059669,
                    #10b981
                );

            font-size: 13px;
            font-weight: 800;

            box-shadow:
                0 8px 18px rgba(16,185,129,0.18);

            transition: all 0.2s ease;
        }

        .done-btn:hover {
            transform: translateY(-2px);

            box-shadow:
                0 12px 23px rgba(16,185,129,0.25);
        }

        /* =========================================================
           PROVIDER LIST
        ========================================================= */

        .provider-list-wrap {
            padding: 0 30px 24px;
        }

        #providersList {
            min-height: 43px;

            padding: 12px;

            display: flex;
            flex-wrap: wrap;
            gap: 8px;

            border-radius: 15px;

            background: #f8fafc;

            border: 1px solid #e6ebf2;
        }

        .provider-chip {
            display: inline-flex;
            align-items: center;
            gap: 7px;

            padding: 8px 11px;

            border-radius: 10px;

            color: #2563eb;

            background: white;

            border: 1px solid #dbeafe;

            font-size: 11px;
            font-weight: 700;

            box-shadow:
                0 3px 8px rgba(15,23,42,0.04);
        }

        /* =========================================================
           ROUTING SECTION
        ========================================================= */

        .routing-section {
            padding: 25px 30px 30px;

            border-top: 1px solid #e8edf5;
        }

        .routing-heading {
            display: flex;
            align-items: center;
            gap: 10px;

            margin-bottom: 19px;
        }

        .routing-heading-icon {
            width: 36px;
            height: 36px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 11px;

            color: #7c3aed;

            background: #f5f3ff;
            border: 1px solid #e9d5ff;
        }

        .routing-heading h2 {
            margin: 0;

            color: #172033;

            font-size: 17px;
            font-weight: 850;
        }

        .routing-heading p {
            margin: 3px 0 0;

            color: #94a3b8;

            font-size: 11px;
        }

        .routing-grid {
            display: grid;

            grid-template-columns:
                repeat(3, minmax(0, 1fr));

            gap: 15px;
        }

        .routing-card {
            position: relative;

            overflow: hidden;

            padding: 20px;

            border-radius: 19px;

            background: white;

            border: 1px solid #e5eaf1;

            box-shadow:
                0 8px 22px rgba(15,23,42,0.045);

            transition:
                transform 0.22s ease,
                box-shadow 0.22s ease,
                border-color 0.22s ease;
        }

        .routing-card::before {
            content: "";

            position: absolute;

            top: 0;
            left: 0;
            right: 0;

            height: 3px;

            opacity: 0.9;
        }

        .routing-card.low::before {
            background: linear-gradient(90deg, #10b981, #34d399);
        }

        .routing-card.medium::before {
            background: linear-gradient(90deg, #f59e0b, #fbbf24);
        }

        .routing-card.hard::before {
            background: linear-gradient(90deg, #ef4444, #fb7185);
        }

        .routing-card:hover {
            transform: translateY(-4px);

            box-shadow:
                0 16px 32px rgba(15,23,42,0.09);

            border-color: #cbd5e1;
        }

        .level-icon {
            width: 39px;
            height: 39px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 12px;

            margin-bottom: 13px;

            font-size: 14px;
        }

        .low .level-icon {
            color: #059669;
            background: #ecfdf5;
        }

        .medium .level-icon {
            color: #d97706;
            background: #fffbeb;
        }

        .hard .level-icon {
            color: #dc2626;
            background: #fef2f2;
        }

        .routing-card h3 {
            margin: 0;

            font-size: 15px;
            font-weight: 900;

            letter-spacing: 0.5px;
        }

        .low h3 {
            color: #059669;
        }

        .medium h3 {
            color: #d97706;
        }

        .hard h3 {
            color: #dc2626;
        }

        .routing-card p {
            margin: 5px 0 15px;

            color: #94a3b8;

            font-size: 11px;
        }

        .premium-select {
            width: 100%;

            height: 42px;

            padding: 0 11px;

            border-radius: 10px;

            color: #334155;

            background: #f8fafc;

            border: 1px solid #e2e8f0;

            outline: none;

            font-size: 12px;
            font-weight: 600;

            cursor: pointer;

            transition: all 0.2s ease;
        }

        .premium-select:focus {
            border-color: #93c5fd;

            background: white;

            box-shadow:
                0 0 0 4px rgba(59,130,246,0.08);
        }

        /* =========================================================
           PRODUCTION KEY
        ========================================================= */

        .production-section {
            margin: 0 30px 30px;
            padding: 24px;

            border-radius: 21px;

            background:
                linear-gradient(
                    135deg,
                    #101827,
                    #17223a 55%,
                    #202b48
                );

            border: 1px solid rgba(148,163,184,0.18);

            box-shadow:
                0 18px 40px rgba(15,23,42,0.16);

            color: white;
        }

        .production-title {
            display: flex;
            align-items: center;
            gap: 12px;

            margin-bottom: 17px;
        }

        .production-icon {
            width: 40px;
            height: 40px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 12px;

            color: #c4b5fd;

            background: rgba(139,92,246,0.14);

            border: 1px solid rgba(167,139,250,0.20);
        }

        .production-title h2 {
            margin: 0;

            color: white;

            font-size: 16px;
            font-weight: 850;
        }

        .production-title p {
            margin: 3px 0 0;

            color: #94a3b8;

            font-size: 11px;
        }

        .production-input {
            width: 100%;

            min-height: 45px;

            padding: 0 14px;

            color: white;

            background: rgba(255,255,255,0.06);

            border: 1px solid rgba(148,163,184,0.20);

            border-radius: 11px;

            outline: none;

            font-size: 13px;

            transition: all 0.2s ease;
        }

        .production-input::placeholder {
            color: #94a3b8;
        }

        .production-input:focus {
            border-color: rgba(96,165,250,0.65);

            background: rgba(255,255,255,0.08);

            box-shadow:
                0 0 0 4px rgba(59,130,246,0.10);
        }

        .generate-btn {
            min-height: 45px;

            padding: 0 20px;

            border: none;
            border-radius: 11px;

            color: white;

            background:
                linear-gradient(
                    135deg,
                    #7c3aed,
                    #4f46e5
                );

            font-size: 12px;
            font-weight: 850;

            cursor: pointer;

            box-shadow:
                0 10px 24px rgba(124,58,237,0.25);

            transition: all 0.2s ease;
        }

        .generate-btn:hover {
            transform: translateY(-2px);

            box-shadow:
                0 14px 30px rgba(124,58,237,0.34);

            filter: brightness(1.06);
        }

        #keyOutput {
            margin-top: 14px;

            padding: 14px 15px;

            border-radius: 12px;

            color: #86efac;

            background: rgba(0,0,0,0.22);

            border: 1px solid rgba(134,239,172,0.16);

            font-size: 12px;

            line-height: 1.7;

            word-break: break-all;
        }

        /* =========================================================
           FOOTER / BRAND
        ========================================================= */

        .brand-footer {
            padding: 3px 30px 27px;

            text-align: center;
        }

        .footer-brand {
            display: inline-flex;
            align-items: center;
            gap: 7px;

            color: #64748b;

            font-size: 11px;
            font-weight: 700;
        }

        .footer-brand-mark {
            width: 20px;
            height: 20px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 6px;

            color: white;

            background:
                linear-gradient(135deg, #2563eb, #7c3aed);

            font-size: 9px;
            font-weight: 900;
        }

        .footer-brand strong {
            color: #334155;
        }

        /* =========================================================
           LOADING STATE
        ========================================================= */

        .loading-dot {
            display: inline-block;

            width: 6px;
            height: 6px;

            margin-left: 5px;

            border-radius: 50%;

            background: currentColor;

            animation: loadingDot 1s infinite ease-in-out;
        }

        @keyframes loadingDot {
            0%, 80%, 100% {
                opacity: 0.25;
                transform: scale(0.7);
            }

            40% {
                opacity: 1;
                transform: scale(1);
            }
        }

        /* =========================================================
           MOBILE
        ========================================================= */

        @media (max-width: 800px) {

            .app-shell {
                padding: 12px 10px 35px;
            }

            .main-panel {
                border-radius: 20px;
            }

            .top-header {
            overflow: visible;
                padding: 20px 17px;

                align-items: flex-start;

                flex-direction: column;
            }

            .brand-area {
                width: 100%;
            }

            .brand-text h1 {
                font-size: 19px;
            }

            .add-api-btn {
                width: 100%;
            }

            .header-badge {
                display: none;
            }

            .section {
                padding: 20px 17px;
            }

            #providerForm {
                margin: 0 17px 20px;
                padding: 17px;
            }

            .provider-list-wrap {
                padding: 0 17px 20px;
            }

            .routing-section {
                padding: 20px 17px;
            }

            .routing-grid {
                grid-template-columns: 1fr;
            }

            .routing-card {
                padding: 18px;
            }

            .production-section {
                margin: 0 17px 22px;
                padding: 18px;
            }

            .brand-footer {
                padding: 0 17px 22px;
            }
        }

        @media (max-width: 430px) {

            .brand-logo {
                width: 46px;
                height: 46px;

                border-radius: 13px;
            }

            .brand-text h1 {
                font-size: 17px;
            }

            .brand-text p {
                font-size: 10px;
            }

            .opening-logo {
                width: 78px;
                height: 78px;

                font-size: 34px;

                border-radius: 22px;
            }

            .opening-title {
                font-size: 24px;
            }

            .production-section .flex {
                gap: 10px;
            }
        }

    </style>
</head>

<body>

    <!-- =========================================================
         PREMIUM OPENING SCREEN
    ========================================================== -->

    <div id="openingScreen">

        <div class="opening-content">

            <div class="opening-logo">
                S
            </div>

            <div class="opening-title">
                Stratic Soft
            </div>

            <div class="opening-subtitle">
                AI Router Console
            </div>

            <div class="opening-line"></div>

        </div>

    </div>


    <!-- =========================================================
         MAIN APPLICATION
    ========================================================== -->

    <div class="app-shell">

        <div class="main-panel">

            <div class="content-layer">


                <!-- =================================================
                     HEADER
                ================================================== -->

                <div class="top-header">

                    <div class="brand-area">

                        <div class="brand-logo">
                            S
                        </div>

                        <div class="brand-text">

                            <h1>
                                AI Router Console
                            </h1>

                            <p>
                                STRATIC SOFT • AI INFRASTRUCTURE
                            </p>

                        </div>

                    </div>


                    <div class="flex items-center gap-3">

                        <div class="header-badge">
                            <span class="status-dot"></span>
                            System Ready
                        </div>

                        <!-- Three Dot History Menu -->
                        <div class="relative" style="overflow:visible;">
                            <button onclick="toggleHistoryMenu(event)" class="w-10 h-10 rounded-xl bg-white border border-slate-200 flex items-center justify-center hover:bg-slate-50 transition shadow-sm">
                                <i class="fa-solid fa-ellipsis-vertical text-slate-600 text-lg"></i>
                            </button>

                            <div id="historyMenu" class="hidden absolute left-0 top-full mt-2 w-56 bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden" style="min-width:220px; z-index:9999;">
                                <button onclick="openApiKeysHistory()" class="w-full text-left px-4 py-3.5 hover:bg-slate-50 flex items-center gap-3 text-sm font-semibold text-slate-700">
                                    <i class="fa-solid fa-key text-blue-500 w-5 text-center"></i>
                                    API Keys History
                                </button>
                                <button onclick="openProductionHistory()" class="w-full text-left px-4 py-3.5 hover:bg-slate-50 flex items-center gap-3 text-sm font-semibold text-slate-700 border-t border-slate-100">
                                    <i class="fa-solid fa-building text-purple-500 w-5 text-center"></i>
                                    Production Keys History
                                </button>
                            </div>
                        </div>

                        <button
                            onclick="toggleProviderForm()"
                            class="add-api-btn">

                            <i class="fa-solid fa-plus"></i>

                            Add API Key

                        </button>

                    </div>

                </div>


                <!-- =================================================
                     PROVIDER FORM
                ================================================== -->

                <div id="providerForm" class="hidden">

                    <div class="form-heading">

                        <i class="fa-solid fa-plug-circle-plus"></i>

                        <h2>
                            Add & Verify Provider
                        </h2>

                    </div>


                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

                        <input
                            id="name"
                            placeholder="Provider Name (e.g. Groq, OpenAI)"
                            class="premium-input">


                        <input
                            id="api_key"
                            type="password"
                            placeholder="Enter Your API Key"
                            class="premium-input">


                        <input
                            id="model_name"
                            placeholder="Enter Your Model (e.g. gpt-4o, llama-3.3-70b)"
                            class="premium-input">


                        <input
                            id="base_url"
                            placeholder="Enter Your URL"
                            value="https://api.openai.com/v1"
                            class="premium-input">

                    </div>


                    <div class="mt-5 flex items-center gap-4">

                        <button
                            onclick="verifyAndSaveProvider()"
                            class="done-btn">

                            <i class="fa-solid fa-check mr-1"></i>

                            Done

                        </button>

                        <div
                            id="checkResult"
                            class="text-sm font-bold">
                        </div>

                    </div>

                </div>


                <!-- =================================================
                     SAVED API KEYS
                ================================================== -->

                <div class="provider-list-wrap">

                    <div class="section-title">

                        <div class="section-title-icon">
                            <i class="fa-solid fa-key"></i>
                        </div>

                        <h3>
                            Available API Keys
                        </h3>

                    </div>

                    <div id="providersList">

                        <span class="text-slate-400 text-xs">
                            Loading providers...
                        </span>

                    </div>

                </div>


                <!-- =================================================
                     ROUTING
                ================================================== -->

                <div class="routing-section">

                    <div class="routing-heading">

                        <div class="routing-heading-icon">
                            <i class="fa-solid fa-route"></i>
                        </div>

                        <div>

                            <h2>
                                Word Limit Mapping & Routing
                            </h2>

                            <p>
                                Configure intelligent model routing by response complexity
                            </p>

                        </div>

                    </div>


                    <div class="routing-grid">


                        <!-- LOW -->

                        <div class="routing-card low">

                            <div class="level-icon">
                                <i class="fa-solid fa-bolt"></i>
                            </div>

                            <h3>
                                LOW
                            </h3>

                            <p>
                                20 शब्द +
                            </p>

                            <select
                                id="low_select"
                                class="premium-select">
                            </select>

                        </div>


                        <!-- MEDIUM -->

                        <div class="routing-card medium">

                            <div class="level-icon">
                                <i class="fa-solid fa-layer-group"></i>
                            </div>

                            <h3>
                                MEDIUM
                            </h3>

                            <p>
                                50 शब्द +
                            </p>

                            <select
                                id="medium_select"
                                class="premium-select">
                            </select>

                        </div>


                        <!-- HARD -->

                        <div class="routing-card hard">

                            <div class="level-icon">
                                <i class="fa-solid fa-brain"></i>
                            </div>

                            <h3>
                                HARD
                            </h3>

                            <p>
                                100 शब्द +
                            </p>

                            <select
                                id="hard_select"
                                class="premium-select">
                            </select>

                        </div>

                    </div>

                </div>


                <!-- =================================================
                     PRODUCTION KEY
                ================================================== -->

                <div class="production-section">

                    <div class="production-title">

                        <div class="production-icon">
                            <i class="fa-solid fa-shield-halved"></i>
                        </div>

                        <div>

                            <h2>
                                Generate Production Key
                            </h2>

                            <p>
                                Create a secure production access key for your company
                            </p>

                        </div>

                    </div>


                    <div class="flex flex-col md:flex-row gap-3 mb-4">

                        <input
                            id="company_name"
                            placeholder="Company Name"
                            class="production-input flex-1">


                        <button
                            onclick="generateProductionKey()"
                            class="generate-btn">

                            <i class="fa-solid fa-key mr-2"></i>

                            Generate Production Key

                        </button>

                    </div>


                    <div
                        id="keyOutput"
                        class="hidden font-mono break-all">
                    </div>

                </div>


                <!-- =================================================
                     STRATIC SOFT FOOTER
                ================================================== -->

                <div class="brand-footer">

                    <div class="footer-brand">

                        <span class="footer-brand-mark">
                            S
                        </span>

                        Powered by
                        <strong>
                            Stratic Soft
                        </strong>

                    </div>

                </div>


            </div>

        </div>

    </div>


    <!-- =========================================================
         HISTORY MODALS
    ========================================================== -->

    <!-- API Keys History Modal -->
    <div id="apiKeysModal" class="fixed inset-0 bg-black/40 z-[9999] hidden items-center justify-center p-4" style="display:none;">
        <div class="bg-white rounded-3xl w-full max-w-lg max-h-[80vh] overflow-hidden shadow-2xl">
            <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <h3 class="font-bold text-lg text-slate-800">API Keys History</h3>
                <button onclick="closeApiKeysHistory()" class="w-9 h-9 rounded-full hover:bg-slate-100 flex items-center justify-center">
                    <i class="fa-solid fa-xmark text-slate-500"></i>
                </button>
            </div>
            <div id="apiKeysList" class="p-4 overflow-y-auto max-h-[60vh] space-y-2">
            </div>
        </div>
    </div>

    <!-- Production Keys History Modal -->
    <div id="productionModal" class="fixed inset-0 bg-black/40 z-[9999] hidden items-center justify-center p-4" style="display:none;">
        <div class="bg-white rounded-3xl w-full max-w-lg max-h-[80vh] overflow-hidden shadow-2xl">
            <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                <h3 class="font-bold text-lg text-slate-800">Production Keys History</h3>
                <button onclick="closeProductionHistory()" class="w-9 h-9 rounded-full hover:bg-slate-100 flex items-center justify-center">
                    <i class="fa-solid fa-xmark text-slate-500"></i>
                </button>
            </div>
            <div id="productionList" class="p-4 overflow-y-auto max-h-[60vh] space-y-2">
            </div>
        </div>
    </div>


    <!-- =========================================================
         JAVASCRIPT
         EXISTING FUNCTIONALITY PRESERVED
    ========================================================== -->

    <script>

        /* =========================================================
           OPENING SCREEN
        ========================================================= */

        // Force hide opening screen - multiple fallbacks so it always disappears
        function hideOpeningScreen() {
            var screen = document.getElementById("openingScreen");
            if (screen) {
                screen.classList.add("hide");
                screen.style.display = "none";
                screen.style.visibility = "hidden";
                screen.style.opacity = "0";
                screen.style.pointerEvents = "none";
                screen.style.zIndex = "-1";
            }
        }
        // Run at several timings so one of them will catch
        setTimeout(hideOpeningScreen, 800);
        setTimeout(hideOpeningScreen, 1500);
        setTimeout(hideOpeningScreen, 2500);
        if (document.readyState === "complete") {
            setTimeout(hideOpeningScreen, 400);
        } else {
            window.addEventListener("load", function() {
                setTimeout(hideOpeningScreen, 400);
            });
        }
        document.addEventListener("DOMContentLoaded", function() {
            setTimeout(hideOpeningScreen, 300);
        });


        /* =========================================================
           PROVIDER FORM
        ========================================================= */

        function toggleProviderForm() {

            document
                .getElementById('providerForm')
                .classList
                .toggle('hidden');

        }


        /* =========================================================
           VERIFY & SAVE PROVIDER
        ========================================================= */

        async function verifyAndSaveProvider() {

            const checkResult =
                document.getElementById('checkResult');

            checkResult.className =
                "text-sm font-bold text-yellow-600 flex items-center gap-2";

            checkResult.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Checking credentials...';


            const data = {

                name:
                    document.getElementById('name').value,

                api_key:
                    document.getElementById('api_key').value,

                base_url:
                    document.getElementById('base_url').value,

                model_name:
                    document.getElementById('model_name').value

            };


            try {

                const res = await fetch(
                    '/admin/providers/verify-and-add',
                    {
                        method: 'POST',

                        headers: {
                            'Content-Type':
                                'application/json'
                        },

                        body:
                            JSON.stringify(data)
                    }
                );


                const result =
                    await res.json();


                if (res.ok && result.valid) {

                    checkResult.className =
                        "text-sm font-bold text-green-600 flex items-center gap-1";

                    checkResult.innerHTML =
                        '<i class="fa-solid fa-circle-check"></i> Yes (Verified & Saved)';

                    loadProviders();

                } else {

                    checkResult.className =
                        "text-sm font-bold text-red-600";

                    checkResult.innerText =
                        "❌ Invalid Credentials";

                }

            } catch (error) {

                checkResult.className =
                    "text-sm font-bold text-red-600";

                checkResult.innerText =
                    "❌ Connection Error";

            }

        }


        /* =========================================================
           HISTORY MENU + DELETE SYSTEM
        ========================================================== */

        function toggleHistoryMenu(event) {
            if (event) event.stopPropagation();
            const menu = document.getElementById('historyMenu');
            menu.classList.toggle('hidden');
        }

        document.addEventListener('click', function(e) {
            const menu = document.getElementById('historyMenu');
            if (menu && !e.target.closest('.relative')) {
                menu.classList.add('hidden');
            }
            // close item menus
            document.querySelectorAll('[id^="api-menu-"], [id^="prod-menu-"]').forEach(el => {
                if (!e.target.closest('[id^="api-menu-"]') && !e.target.closest('[id^="prod-menu-"]') && !e.target.closest('button')) {
                    el.classList.add('hidden');
                }
            });
        });

        function openApiKeysHistory() {
            document.getElementById('historyMenu').classList.add('hidden');
            const modal = document.getElementById('apiKeysModal');
            modal.style.display = 'flex';
            modal.classList.remove('hidden');
            loadApiKeysHistory();
        }

        function closeApiKeysHistory() {
            const modal = document.getElementById('apiKeysModal');
            modal.style.display = 'none';
            modal.classList.add('hidden');
        }

        async function loadApiKeysHistory() {
            const list = document.getElementById('apiKeysList');
            list.innerHTML = '<div class="text-center text-slate-400 py-10"><i class="fa-solid fa-spinner fa-spin text-2xl"></i></div>';

            try {
                const res = await fetch('/admin/providers');
                const providers = await res.json();

                if (!providers || providers.length === 0) {
                    list.innerHTML = '<p class="text-center text-slate-400 py-10 text-sm">No API Keys found</p>';
                    return;
                }

                list.innerHTML = providers.map(p => `
                    <div class="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-slate-100 transition group">
                        <div class="flex-1 min-w-0 pr-3">
                            <div class="font-semibold text-slate-800 truncate">${p.name || 'Unnamed'}</div>
                            <div class="text-xs text-slate-500 truncate mt-0.5">${p.model_name || ''}</div>
                        </div>
                        <div class="relative">
                            <button onclick="toggleItemMenu(event, 'api-menu-${p.id}')" class="w-8 h-8 rounded-lg hover:bg-white flex items-center justify-center text-slate-500">
                                <i class="fa-solid fa-ellipsis-vertical"></i>
                            </button>
                            <div id="api-menu-${p.id}" class="hidden absolute right-0 top-9 w-36 bg-white rounded-xl shadow-lg border border-slate-100 z-20 overflow-hidden">
                                <button onclick="deleteApiKey(${p.id})" class="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 font-medium">
                                    <i class="fa-solid fa-trash text-xs"></i> Delete
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                list.innerHTML = '<p class="text-center text-red-500 py-10 text-sm">Failed to load API Keys</p>';
            }
        }

        async function deleteApiKey(id) {
            if (!confirm('Delete this API Key? This cannot be undone.')) return;

            try {
                const res = await fetch('/admin/providers/' + id, { method: 'DELETE' });
                if (res.ok) {
                    loadApiKeysHistory();
                    if (typeof loadProviders === 'function') loadProviders();
                } else {
                    alert('Delete failed. Please try again.');
                }
            } catch (e) {
                alert('Error while deleting API Key');
            }
        }

        function openProductionHistory() {
            document.getElementById('historyMenu').classList.add('hidden');
            const modal = document.getElementById('productionModal');
            modal.style.display = 'flex';
            modal.classList.remove('hidden');
            loadProductionHistory();
        }

        function closeProductionHistory() {
            const modal = document.getElementById('productionModal');
            modal.style.display = 'none';
            modal.classList.add('hidden');
        }

        async function loadProductionHistory() {
            const list = document.getElementById('productionList');
            list.innerHTML = '<div class="text-center text-slate-400 py-10"><i class="fa-solid fa-spinner fa-spin text-2xl"></i></div>';

            try {
                const res = await fetch('/admin/product-keys');
                const keys = await res.json();

                if (!keys || keys.length === 0) {
                    list.innerHTML = '<p class="text-center text-slate-400 py-10 text-sm">No Production Keys found</p>';
                    return;
                }

                list.innerHTML = keys.map(k => `
                    <div class="flex items-center justify-between p-3.5 rounded-2xl bg-slate-50 hover:bg-slate-100 transition">
                        <div class="flex-1 min-w-0 pr-3">
                            <div class="font-semibold text-slate-800 truncate">${k.company_name || 'Unnamed Company'}</div>
                            <div class="text-xs text-slate-500 font-mono truncate mt-0.5">${(k.key || '').substring(0, 28)}...</div>
                        </div>
                        <div class="relative">
                            <button onclick="toggleItemMenu(event, 'prod-menu-${k.id}')" class="w-8 h-8 rounded-lg hover:bg-white flex items-center justify-center text-slate-500">
                                <i class="fa-solid fa-ellipsis-vertical"></i>
                            </button>
                            <div id="prod-menu-${k.id}" class="hidden absolute right-0 top-9 w-36 bg-white rounded-xl shadow-lg border border-slate-100 z-20 overflow-hidden">
                                <button onclick="deleteProductionKey(${k.id})" class="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2 font-medium">
                                    <i class="fa-solid fa-trash text-xs"></i> Delete
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                list.innerHTML = '<p class="text-center text-red-500 py-10 text-sm">Failed to load Production Keys</p>';
            }
        }

        async function deleteProductionKey(id) {
            if (!confirm('Delete this Production Key? This cannot be undone.')) return;

            try {
                const res = await fetch('/admin/product-keys/' + id, { method: 'DELETE' });
                if (res.ok) {
                    loadProductionHistory();
                } else {
                    alert('Delete failed. Please try again.');
                }
            } catch (e) {
                alert('Error while deleting Production Key');
            }
        }

        function toggleItemMenu(event, id) {
            event.stopPropagation();
            document.querySelectorAll('[id^="api-menu-"], [id^="prod-menu-"]').forEach(el => {
                if (el.id !== id) el.classList.add('hidden');
            });
            const el = document.getElementById(id);
            if (el) el.classList.toggle('hidden');
        }


        /* =========================================================
           LOAD PROVIDERS
        ========================================================== */

        async function loadProviders() {

            try {

                const res =
                    await fetch('/admin/providers');

                const data =
                    await res.json();


                let listHtml = '';

                let optionsHtml =
                    '<option value="">Select API Key</option>';


                data.forEach(p => {

                    listHtml += `
                        <span class="provider-chip">
                            <i class="fa-solid fa-circle-check text-emerald-500"></i>
                            ${p.name} (${p.model_name})
                        </span>
                    `;


                    optionsHtml += `
                        <option value="${p.id}">
                            ${p.name} - ${p.model_name}
                        </option>
                    `;

                });


                document.getElementById(
                    'providersList'
                ).innerHTML =
                    listHtml ||
                    "<span class='text-slate-400 text-xs'>No active providers</span>";


                document.getElementById(
                    'low_select'
                ).innerHTML =
                    optionsHtml;


                document.getElementById(
                    'medium_select'
                ).innerHTML =
                    optionsHtml;


                document.getElementById(
                    'hard_select'
                ).innerHTML =
                    optionsHtml;


            } catch (error) {

                document.getElementById(
                    'providersList'
                ).innerHTML =
                    "<span class='text-red-400 text-xs'>Unable to load providers</span>";

            }

        }


        /* =========================================================
           GENERATE PRODUCTION KEY
        ========================================================== */

        async function generateProductionKey() {

            const company =
                document.getElementById(
                    'company_name'
                ).value;


            const low =
                document.getElementById(
                    'low_select'
                ).value;


            const medium =
                document.getElementById(
                    'medium_select'
                ).value;


            const hard =
                document.getElementById(
                    'hard_select'
                ).value;


            if (
                !company ||
                !low ||
                !medium ||
                !hard
            ) {

                alert(
                    "कृपया कंपनी का नाम और तीनों लेवल्स के लिए API Keys चुनें!"
                );

                return;

            }


            const data = {

                company_name:
                    company,

                low_provider_id:
                    parseInt(low),

                medium_provider_id:
                    parseInt(medium),

                hard_provider_id:
                    parseInt(hard)

            };


            try {

                const res =
                    await fetch(
                        '/admin/product-key',
                        {
                            method: 'POST',

                            headers: {
                                'Content-Type':
                                    'application/json'
                            },

                            body:
                                JSON.stringify(data)
                        }
                    );


                const result =
                    await res.json();


                const out =
                    document.getElementById(
                        'keyOutput'
                    );


                out.classList.remove(
                    'hidden'
                );


                out.innerText =
                    "Production Key: " +
                    result.product_key;


            } catch (error) {

                alert(
                    "Production Key generate करने में समस्या आई।"
                );

            }

        }


        /* =========================================================
           INITIAL LOAD
        ========================================================== */

        loadProviders();

    </script>

</body>
</html>
"""