import re

NEW_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Sentiment Analysis</title>

    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">

    <!-- Stylesheet (No Tailwind) -->
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">

    <!-- Chart.js & WordCloud -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/wordcloud2.js/1.2.2/wordcloud2.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
</head>

<body>
    <!-- Sidebar -->
    <aside class="app-sidebar">
        <div>
            <!-- Logo -->
            <div class="sidebar-header">
                <div class="brand-icon"><i class="fa-solid fa-brain"></i></div>
                <span class="brand-text hide-on-mobile">Insight <span>AI</span></span>
            </div>

            <!-- Navigation -->
            <nav class="sidebar-nav">
                <button onclick="switchTab('dashboard')" id="nav-dashboard" class="nav-item active">
                    <i class="fa-solid fa-chart-pie nav-icon"></i>
                    <span class="hide-on-mobile">Dashboard</span>
                </button>
                <button onclick="switchTab('analysis')" id="nav-analysis" class="nav-item">
                    <i class="fa-solid fa-magnifying-glass nav-icon"></i>
                    <span class="hide-on-mobile">Analysis</span>
                </button>
                <button onclick="switchTab('comments')" id="nav-comments" class="nav-item">
                    <i class="fa-solid fa-comments nav-icon"></i>
                    <span class="hide-on-mobile">Comments</span>
                </button>
                <button onclick="switchTab('reports')" id="nav-reports" class="nav-item">
                    <i class="fa-solid fa-file-export nav-icon"></i>
                    <span class="hide-on-mobile">Reports</span>
                </button>
            </nav>
        </div>

        <!-- System Status -->
        <div class="sidebar-footer hide-on-mobile">
            <div class="system-status">
                <div class="status-icon"><i class="fa-solid fa-server"></i></div>
                <div class="status-text">
                    <h5>System Status</h5>
                    <div class="status-indicator">
                        <span class="status-dot"></span>
                        <span>Online (VADER)</span>
                    </div>
                </div>
            </div>
        </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
        <!-- Top Bar / Header -->
        <header class="top-header">
            <div id="headerContent">
                <h2 class="header-title" id="pageTitle">Sentiment Analysis for YouTube Comments using AI</h2>
                <p class="header-subtitle" id="pageSubtitle">Analyze public opinion instantly</p>
            </div>
            <div>
                <button class="action-btn"><i class="fa-solid fa-bell"></i></button>
            </div>
        </header>

        <!-- Scrollable Content -->
        <div class="scroll-area" id="scrollArea">

            <!-- VIEW: DASHBOARD -->
            <div id="view-dashboard" class="view-container">

                <!-- Search Section -->
                <div class="card card-padding search-card">
                    <div class="search-icon"><i class="fa-brands fa-youtube"></i></div>
                    <input type="text" id="videoUrl" class="search-input" placeholder="https://youtu.be/...">
                    <button onclick="analyzeVideo()" id="analyzeBtn" class="btn-primary">
                        Analyze Comments <i class="fa-solid fa-wand-magic-sparkles" style="font-size: 0.75rem;"></i>
                    </button>
                </div>

                <!-- Initial Empty State -->
                <div id="emptyState" class="empty-state">
                    <div class="empty-icon"><i class="fa-solid fa-chart-simple"></i></div>
                    <h3 class="empty-title">Ready to Analyze</h3>
                    <p class="empty-desc">Paste a YouTube URL above to view insights.</p>
                </div>

                <!-- Loader -->
                <div id="loader" class="hidden loader-container">
                    <div class="loader-content">
                        <div class="spinner"></div>
                        <span class="loader-text">Analyzing comments...</span>
                    </div>
                </div>

                <!-- Live Stream Mode (Replay) -->
                <div id="liveStreamArea" class="hidden">
                    <div class="live-stream-header" style="margin-bottom: 1.5rem;">
                        <div class="live-stream-title-wrap">
                            <div class="ping-indicator">
                                <span class="ping-anim"></span>
                                <span class="ping-dot"></span>
                            </div>
                            <h2 class="live-stream-title">Live Sentiment Feed</h2>
                        </div>
                        <div class="live-controls">
                            <button onclick="showDashboard()" class="btn-xs btn-dark">DASHBOARD</button>
                            <button onclick="toggleStream(true)" id="btnPauseStream" class="btn-xs btn-light">PAUSE</button>
                            <div class="progress-badge" id="streamProgress">0/0</div>
                        </div>
                    </div>

                    <div class="grid lg-grid-cols-3 gap-6 live-grid">
                        <!-- Left: Real-time Graph -->
                        <div class="card card-padding lg-col-span-2 flex flex-col">
                            <h4 class="live-trend-header">Real-time Sentiment Trend</h4>
                            <div class="live-chart-container">
                                <canvas id="liveTrendChart"></canvas>
                            </div>
                            <div class="live-stats-row">
                                <div class="live-stat-box positive">
                                    <div class="live-stat-label positive">Positive</div>
                                    <div class="live-stat-value positive" id="livePosCount">0</div>
                                </div>
                                <div class="live-stat-box negative">
                                    <div class="live-stat-label negative">Negative</div>
                                    <div class="live-stat-value negative" id="liveNegCount">0</div>
                                </div>
                                <div class="live-stat-box neutral">
                                    <div class="live-stat-label neutral">Neutral</div>
                                    <div class="live-stat-value neutral" id="liveNeuCount">0</div>
                                </div>
                            </div>
                        </div>

                        <!-- Right: Live Chat Box -->
                        <div class="chat-container card">
                            <div class="chat-header">
                                <h4 class="chat-title">Live Chat</h4>
                                <i class="fa-solid fa-comments" style="color: var(--text-light);"></i>
                            </div>
                            <div id="liveChatBox" class="chat-box">
                                <div class="chat-wait-msg">Waiting for stream...</div>
                            </div>
                            <div class="chat-footer">Showing real-time comments</div>
                        </div>
                    </div>
                </div>

                <!-- Analysis Results (Hidden by default, shown after replay or optionally) -->
                <div id="dashboardContent" class="hidden">

                    <!-- Dashboard Header / Switcher -->
                    <div class="flex" style="justify-content: flex-end; margin-bottom: 1.5rem;">
                        <button onclick="startLiveStream(currentData.comments)" class="btn-replay">
                            <i class="fa-solid fa-play"></i> Replay Live Chat
                        </button>
                    </div>

                    <!-- KPI Cards Code -->
                    <div class="grid grid-cols-1 md-grid-cols-2 grid-cols-4 gap-6" style="margin-bottom: 2rem;">
                        <!-- Positive -->
                        <div class="card card-padding kpi-card positive">
                            <div class="kpi-header">
                                <div class="kpi-icon-box"><i class="fa-solid fa-face-smile"></i></div>
                                <span class="kpi-label">Positive</span>
                            </div>
                            <h3 class="kpi-value" id="statPos">--%</h3>
                            <p class="kpi-desc" id="statPosCount">0 comments</p>
                        </div>
                        <!-- Negative -->
                        <div class="card card-padding kpi-card negative">
                            <div class="kpi-header">
                                <div class="kpi-icon-box"><i class="fa-solid fa-face-frown"></i></div>
                                <span class="kpi-label">Negative</span>
                            </div>
                            <h3 class="kpi-value" id="statNeg">--%</h3>
                            <p class="kpi-desc" id="statNegCount">0 comments</p>
                        </div>
                        <!-- Neutral -->
                        <div class="card card-padding kpi-card neutral">
                            <div class="kpi-header">
                                <div class="kpi-icon-box"><i class="fa-solid fa-face-meh"></i></div>
                                <span class="kpi-label">Neutral</span>
                            </div>
                            <h3 class="kpi-value" id="statNeu">--%</h3>
                            <p class="kpi-desc" id="statNeuCount">0 comments</p>
                        </div>
                        <!-- Total -->
                        <div class="card card-padding kpi-card total">
                            <div class="kpi-header">
                                <div class="kpi-icon-box"><i class="fa-solid fa-comments"></i></div>
                                <span class="kpi-label">Total</span>
                            </div>
                            <h3 class="kpi-value" id="statTotal">0</h3>
                            <p class="kpi-desc">Processed</p>
                        </div>
                    </div>

                    <!-- Video & Narrative Row -->
                    <div class="grid grid-cols-1 lg-grid-cols-3 gap-6" style="margin-bottom: 2rem;">
                        <!-- Video Info -->
                        <div class="card card-padding flex flex-col">
                            <div class="video-info-box">
                                <img id="videoThumb" src="" class="video-thumb" alt="Thumbnail">
                                <div class="video-details">
                                    <h4 id="videoTitle" class="video-title">...</h4>
                                    <p id="channelName" class="channel-name">...</p>
                                    <div class="video-stats">
                                        <span><i class="fa-solid fa-eye"></i> <span id="viewCount">0</span></span>
                                        <span><i class="fa-solid fa-thumbs-up"></i> <span id="likeCount">0</span></span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Narrative -->
                        <div class="card card-padding lg-col-span-2">
                            <div class="narrative-header">
                                <i class="fa-solid fa-robot narrative-icon"></i>
                                <h4 class="narrative-title">AI Narrative Summary</h4>
                            </div>
                            <p id="narrativeText" class="narrative-text">Analysis required...</p>
                        </div>
                    </div>

                    <!-- Charts Row -->
                    <div class="grid grid-cols-1 lg-grid-cols-2 gap-6">
                        <!-- Donut -->
                        <div class="card card-padding">
                            <h4 class="chart-title">Sentiment Analysis Distribution</h4>
                            <div class="chart-container-donut">
                                <canvas id="sentimentChart"></canvas>
                            </div>
                        </div>

                        <!-- Bar -->
                        <div class="card card-padding">
                            <h4 class="chart-title">Sentiment Count (Bar Chart)</h4>
                            <div class="chart-container-bar">
                                <canvas id="barChart"></canvas>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- VIEW: COMMENTS -->
            <div id="view-comments" class="hidden view-container">
                <!-- AI Prediction Sandbox -->
                <div class="card card-padding sandbox-card">
                    <div class="sandbox-dec-1"></div>
                    <div class="sandbox-dec-2"></div>
                    <div class="sandbox-content">
                        <div class="sandbox-title-wrap">
                            <div class="sandbox-emoji">🧠</div>
                            <h3 class="sandbox-title">AI Prediction Sandbox</h3>
                        </div>
                        <p class="sandbox-desc">Test the model with your own text:</p>
                        <div class="sandbox-input-area">
                            <input type="text" id="sandboxInput" class="sandbox-input" placeholder="Type a comment..." onkeydown="if(event.key === 'Enter') testSentiment()">
                            <button onclick="testSentiment()" class="sandbox-btn">
                                <i class="fa-solid fa-bolt"></i>
                            </button>
                        </div>
                        <!-- Result Bar -->
                        <div id="sandboxResult" class="hidden sandbox-result-wrap">
                            <div class="sandbox-bar-container">
                                <div id="sandboxBar" class="sandbox-bar" style="width: 100%">
                                    <span id="sandboxLabel" class="sandbox-label">PENDING</span>
                                </div>
                                <div class="sandbox-score-overlay">
                                    <span id="sandboxScore" class="sandbox-score">--%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card card-padding">
                    <input type="text" id="tableSearch" onkeyup="filterTable()" placeholder="Search within comments..." class="table-search-input">
                </div>
                <div class="card table-wrapper">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Author</th>
                                <th style="width: 50%;">Comment</th>
                                <th>Sentiment</th>
                                <th>Confidence</th>
                                <th>Age</th>
                            </tr>
                        </thead>
                        <tbody id="commentsTableBody">
                            <!-- Populated by JS -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- VIEW: ANALYSIS -->
            <div id="view-analysis" class="hidden view-container">
                <div class="view-header">
                    <i class="fa-solid fa-magnifying-glass-chart view-icon"></i>
                    <h2 class="view-title">Deep Analysis</h2>
                </div>

                <!-- Trend Chart -->
                <div class="card card-padding">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem;">
                        <div>
                            <h3 class="chart-title" style="margin-bottom: 0.25rem;">Trend Analysis</h3>
                            <p style="color: var(--text-muted); font-size: 0.875rem;">Sentiment evolution over time for this video.</p>
                        </div>
                        <div style="display: flex; gap: 1rem; font-size: 0.75rem; font-weight: 500;">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="width: 2rem; height: 0.25rem; background: #bbf7d0; border: 1px solid #22c55e;"></span>
                                <span style="color: var(--text-muted);">Positive Volume</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="width: 2rem; height: 0.25rem; background: #fecaca; border: 1px solid #ef4444;"></span>
                                <span style="color: var(--text-muted);">Negative Volume</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="width: 2rem; height: 0.25rem; background: #e2e8f0; border: 1px solid #64748b;"></span>
                                <span style="color: var(--text-muted);">Neutral Volume</span>
                            </div>
                        </div>
                    </div>
                    <div class="trend-chart-container">
                        <canvas id="trendChart"></canvas>
                    </div>
                </div>

                <!-- Top Comments -->
                <div class="grid grid-cols-1 md-grid-cols-2 gap-6">
                    <div class="card card-padding top-comment-card positive">
                        <h4 class="top-comment-title">Top Positive Comment</h4>
                        <div id="topPositiveContent">
                            <div style="color: var(--text-light); font-style: italic;">No positive comments found.</div>
                        </div>
                    </div>
                    <div class="card card-padding top-comment-card negative">
                        <h4 class="top-comment-title">Top Negative Comment</h4>
                        <div id="topNegativeContent">
                            <div style="color: var(--text-light); font-style: italic;">No negative comments found.</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- VIEW: REPORTS -->
            <div id="view-reports" class="hidden view-container" style="max-width: 60rem;">
                <div class="view-header">
                    <i class="fa-solid fa-file-export view-icon"></i>
                    <h2 class="view-title">Project Reports</h2>
                </div>

                <div class="grid grid-cols-1 md-grid-cols-2 gap-6">
                    <!-- Export Summary Card -->
                    <div class="card card-padding export-card">
                        <div>
                            <h3 class="chart-title">Export Summary</h3>
                            <p class="export-desc">Download the analysis report in PDF or CSV format used for your project submission.</p>
                        </div>
                        <div class="btn-group">
                            <button onclick="downloadReportPDF()" class="btn-export-pdf"><i class="fa-solid fa-file-pdf"></i> Download PDF</button>
                            <button onclick="downloadReportCSV()" class="btn-export-csv"><i class="fa-solid fa-file-csv"></i> Download CSV</button>
                        </div>
                    </div>

                    <!-- Model Metrics Card -->
                    <div class="card card-padding">
                        <h3 class="chart-title">Model Metrics</h3>
                        <div class="metrics-list">
                            <div class="metric-item"><span class="metric-label">• Model:</span><span>VADER (Valence Aware Dictionary)</span></div>
                            <div class="metric-item"><span class="metric-label">• Precision:</span><span>~85% (Social Media Text)</span></div>
                            <div class="metric-item"><span class="metric-label">• Processing:</span><span>&lt; 20ms per comment</span></div>
                            <div class="metric-item"><span class="metric-label">• Status:</span><span class="metric-value active">Active & Live</span></div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </main>

"""

with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract only JS from the original text
js_match = re.search(r'<script.*?>\s*// --- LOGIC ---.*?</script>', text, re.DOTALL)
if js_match:
    js_content = js_match.group(0)
    final_html = NEW_HTML + f"    {js_content}\n</body>\n</html>"
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("Successfully replaced templates/index.html with Vanilla CSS version.")
else:
    print("JS logic block not found. Could not rewrite index.html")
