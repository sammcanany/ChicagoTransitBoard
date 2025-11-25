// Chicago Transit Board - Config Portal
// Loaded from jsDelivr CDN: https://cdn.jsdelivr.net/gh/sammcanany/ChicagoTransitBoard@main/web/config.js

(function() {
    'use strict';

    let config = {};
    let status = {};
    let currentPage = 'main-page';
    let pageStack = [];

    document.addEventListener('DOMContentLoaded', init);

    async function init() {
        try {
            document.getElementById('app').innerHTML = '<div class="loading">Loading configuration...</div>';
            
            const [configRes, statusRes] = await Promise.all([
                fetch('/api/config'),
                fetch('/api/status')
            ]);
            
            config = await configRes.json();
            status = await statusRes.json();
            
            render();
            if (typeof lucide !== 'undefined') lucide.createIcons();
        } catch (error) {
            document.getElementById('app').innerHTML = `
                <div class="error">
                    <h2>Connection Error</h2>
                    <p>Could not connect to board</p>
                    <p>${error.message}</p>
                    <button onclick="location.reload()">Retry</button>
                </div>`;
        }
    }

    function render() {
        const c = config;
        const s = status;
        
        document.getElementById('app').innerHTML = `
            <div id="main-page" class="page">
                <div class="header">
                    <button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button>
                    <div class="header-title">Settings</div>
                </div>
                <div class="status-card">
                    <div class="status-grid">
                        <div class="status-item"><div class="status-label">Status</div><div class="status-value ${s.wifi_connected?'online':''}">${s.wifi_connected?'Online':'Offline'}</div></div>
                        <div class="status-item"><div class="status-label">Version</div><div class="status-value">${s.version||'?'}</div></div>
                        <div class="status-item"><div class="status-label">Uptime</div><div class="status-value">${s.uptime||'0m'}</div></div>
                        <div class="status-item"><div class="status-label">Memory</div><div class="status-value">${s.memory_pct||0}%</div></div>
                    </div>
                </div>
                <div class="menu-list">
                    <div class="menu-item" onclick="TC.nav('wifi')">
                        <div class="menu-icon" style="background:#e3f2fd;color:#1976d2;"><i data-lucide="wifi"></i></div>
                        <div class="menu-content"><div class="menu-title">WiFi</div><div class="menu-subtitle">${c.wifi_ssid||'Not set'}</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('api')">
                        <div class="menu-icon" style="background:#fff3e0;color:#f57c00;"><i data-lucide="key"></i></div>
                        <div class="menu-content"><div class="menu-title">API Keys</div><div class="menu-subtitle">Metra & CTA</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('transit')">
                        <div class="menu-icon" style="background:#e8f5e9;color:#388e3c;"><i data-lucide="train-front"></i></div>
                        <div class="menu-content"><div class="menu-title">Transit</div><div class="menu-subtitle">${c.line_name||'Not set'}</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('display')">
                        <div class="menu-icon" style="background:#f3e5f5;color:#7b1fa2;"><i data-lucide="monitor"></i></div>
                        <div class="menu-content"><div class="menu-title">Display</div><div class="menu-subtitle">Brightness & timing</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('features')">
                        <div class="menu-icon" style="background:#fce4ec;color:#c2185b;"><i data-lucide="settings"></i></div>
                        <div class="menu-content"><div class="menu-title">Features</div><div class="menu-subtitle">Alerts & updates</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('weather')">
                        <div class="menu-icon" style="background:#e0f7fa;color:#0097a7;"><i data-lucide="cloud-sun"></i></div>
                        <div class="menu-content"><div class="menu-title">Weather</div><div class="menu-subtitle">${c.enable_weather?'Enabled':'Disabled'}</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                    <div class="menu-item" onclick="TC.nav('system')">
                        <div class="menu-icon" style="background:#fff9c4;color:#f57f17;"><i data-lucide="cpu"></i></div>
                        <div class="menu-content"><div class="menu-title">System</div><div class="menu-subtitle">LED, sleep & power</div></div>
                        <div class="menu-arrow">›</div>
                    </div>
                </div>
                <div class="action-buttons">
                    <button class="btn btn-secondary" onclick="location.reload()">Refresh</button>
                    <button class="btn btn-primary" onclick="TC.save()">Save All</button>
                </div>
            </div>

            <div id="wifi" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">WiFi</div></div>
                <div class="form-section">
                    <div class="form-group"><label>Network Name</label><input type="text" id="wifi_ssid" value="${c.wifi_ssid||''}"></div>
                    <div class="form-group"><label>Password</label><input type="password" id="wifi_password" placeholder="Leave blank to keep current"></div>
                </div>
            </div>

            <div id="api" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">API Keys</div></div>
                <div class="form-section">
                    <div class="section-title">Metra</div>
                    <div class="form-group"><label>API Token</label><input type="text" id="metra_token" value="${c.metra_token||''}"><div class="help-text">Get from metra.com/developers</div></div>
                </div>
                <div class="form-section">
                    <div class="section-title">CTA</div>
                    <div class="form-group"><label>API Key</label><input type="text" id="cta_token" value="${c.cta_token||''}"><div class="help-text">Get from transitchicago.com/developers</div></div>
                </div>
            </div>

            <div id="transit" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">Transit Lines</div></div>
                <div class="form-section">
                    <div class="form-group">
                        <label>Line</label>
                        <select id="line_select" onchange="TC.updateLine()">
                            <option value="">-- Select --</option>
                            <optgroup label="Metra">
                                <option value="UP-N|Union Pacific North" ${c.line_id==='UP-N'?'selected':''}>UP-N</option>
                                <option value="UP-NW|Union Pacific Northwest" ${c.line_id==='UP-NW'?'selected':''}>UP-NW</option>
                                <option value="UP-W|Union Pacific West" ${c.line_id==='UP-W'?'selected':''}>UP-W</option>
                                <option value="MD-N|Milwaukee District North" ${c.line_id==='MD-N'?'selected':''}>MD-N</option>
                                <option value="MD-W|Milwaukee District West" ${c.line_id==='MD-W'?'selected':''}>MD-W</option>
                                <option value="BNSF|BNSF Railway" ${c.line_id==='BNSF'?'selected':''}>BNSF</option>
                                <option value="ME|Metra Electric" ${c.line_id==='ME'?'selected':''}>ME</option>
                                <option value="RI|Rock Island" ${c.line_id==='RI'?'selected':''}>RI</option>
                                <option value="SWS|SouthWest Service" ${c.line_id==='SWS'?'selected':''}>SWS</option>
                            </optgroup>
                            <optgroup label="CTA">
                                <option value="Red|Red Line" ${c.line_id==='Red'?'selected':''}>Red</option>
                                <option value="Blue|Blue Line" ${c.line_id==='Blue'?'selected':''}>Blue</option>
                                <option value="Brown|Brown Line" ${c.line_id==='Brown'?'selected':''}>Brown</option>
                                <option value="Green|Green Line" ${c.line_id==='Green'?'selected':''}>Green</option>
                                <option value="Orange|Orange Line" ${c.line_id==='Orange'?'selected':''}>Orange</option>
                                <option value="Pink|Pink Line" ${c.line_id==='Pink'?'selected':''}>Pink</option>
                                <option value="Purple|Purple Line" ${c.line_id==='Purple'?'selected':''}>Purple</option>
                            </optgroup>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Station</label>
                        <select id="station_select" onchange="TC.updateStation()">
                            <option value="">-- Select --</option>
                            <optgroup label="Metra">
                                <option value="RAVENSWOOD|Ravenswood" ${c.station_id==='RAVENSWOOD'?'selected':''}>Ravenswood</option>
                                <option value="CLYBOURN|Clybourn" ${c.station_id==='CLYBOURN'?'selected':''}>Clybourn</option>
                                <option value="OTC|Ogilvie" ${c.station_id==='OTC'?'selected':''}>Ogilvie</option>
                                <option value="CUS|Union Station" ${c.station_id==='CUS'?'selected':''}>Union Station</option>
                                <option value="EVANSTON|Evanston" ${c.station_id==='EVANSTON'?'selected':''}>Evanston</option>
                            </optgroup>
                            <optgroup label="CTA">
                                <option value="40900|Howard" ${c.station_id==='40900'?'selected':''}>Howard</option>
                                <option value="41450|95th" ${c.station_id==='41450'?'selected':''}>95th/Dan Ryan</option>
                                <option value="40730|O'Hare" ${c.station_id==='40730'?'selected':''}>O'Hare</option>
                            </optgroup>
                        </select>
                    </div>
                    <input type="hidden" id="line_id" value="${c.line_id||''}">
                    <input type="hidden" id="line_name" value="${c.line_name||''}">
                    <input type="hidden" id="station_id" value="${c.station_id||''}">
                    <input type="hidden" id="station_name" value="${c.station_name||''}">
                </div>
            </div>

            <div id="display" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">Display</div></div>
                <div class="form-section">
                    <div class="form-group">
                        <label>Brightness</label>
                        <div style="display:flex;align-items:center;gap:12px;">
                            <input type="range" id="brightness" min="0.1" max="1.0" step="0.1" value="${c.brightness||0.5}" oninput="document.getElementById('bv').textContent=Math.round(this.value*100)+'%'" style="flex:1">
                            <span id="bv" style="min-width:45px;font-weight:600">${Math.round((c.brightness||0.5)*100)}%</span>
                        </div>
                    </div>
                    <div class="form-group"><label>Rotation Time (sec)</label><input type="number" id="rotation_time" min="1" max="30" value="${c.rotation_time||5}"></div>
                    <div class="form-group"><label>Update Interval (sec)</label><input type="number" id="update_interval" min="10" max="300" value="${c.update_interval||30}"></div>
                    <div class="form-group"><label>Trains to Show</label><input type="number" id="num_trains" min="1" max="8" value="${c.num_trains||4}"></div>
                </div>
            </div>

            <div id="features" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">Features</div></div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Service Alerts</label><label class="toggle-switch"><input type="checkbox" id="enable_service_alerts" ${c.enable_service_alerts?'checked':''}><span class="toggle-slider"></span></label></div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Alert Icons</label><label class="toggle-switch"><input type="checkbox" id="enable_alert_icons" ${c.enable_alert_icons?'checked':''}><span class="toggle-slider"></span></label></div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Auto-Update</label><label class="toggle-switch"><input type="checkbox" id="enable_auto_update" ${c.enable_auto_update?'checked':''}><span class="toggle-slider"></span></label></div>
                </div>
            </div>

            <div id="weather" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">Weather</div></div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Enable Weather</label><label class="toggle-switch"><input type="checkbox" id="enable_weather" ${c.enable_weather?'checked':''}><span class="toggle-slider"></span></label></div>
                </div>
                <div class="form-section">
                    <div class="form-group"><label>Service</label><select id="weather_api_service"><option value="weathergov" ${c.weather_api_service==='weathergov'?'selected':''}>Weather.gov</option><option value="openweathermap" ${c.weather_api_service==='openweathermap'?'selected':''}>OpenWeatherMap</option></select></div>
                    <div class="form-group"><label>ZIP Code</label><input type="text" id="weather_zip_code" value="${c.weather_zip_code||''}" placeholder="60601"></div>
                    <div class="form-group"><label>API Key (OWM)</label><input type="password" id="weather_api_key" value="${c.weather_api_key||''}"></div>
                </div>
            </div>

            <div id="system" class="page hidden">
                <div class="header"><button class="back-btn" onclick="TC.back()"><i data-lucide="chevron-left"></i></button><div class="header-title">System</div></div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Watchdog Timer</label><label class="toggle-switch"><input type="checkbox" id="enable_watchdog" ${c.enable_watchdog?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Auto-reboot if system hangs</div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Status LED</label><label class="toggle-switch"><input type="checkbox" id="enable_status_led" ${c.enable_status_led?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">RGB LED shows connection status</div>
                </div>
                <div class="form-section">
                    <div class="toggle-group"><label class="toggle-label">Sleep Mode</label><label class="toggle-switch"><input type="checkbox" id="enable_sleep_mode" ${c.enable_sleep_mode?'checked':''}><span class="toggle-slider"></span></label></div>
                    <div class="help-text">Dim display at night</div>
                </div>
            </div>
        `;
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }

    function nav(pageId) {
        const cur = document.getElementById(currentPage);
        const next = document.getElementById(pageId);
        pageStack.push(currentPage);
        next.classList.remove('hidden');
        next.style.transform = 'translateX(100%)';
        setTimeout(() => { cur.classList.add('slide-left'); next.style.transform = 'translateX(0)'; }, 10);
        setTimeout(() => { cur.classList.add('hidden'); cur.classList.remove('slide-left'); if(typeof lucide!=='undefined')lucide.createIcons(); }, 300);
        currentPage = pageId;
    }

    function back() {
        if (!pageStack.length) return;
        const cur = document.getElementById(currentPage);
        const prev = document.getElementById(pageStack.pop());
        prev.classList.remove('hidden');
        prev.classList.add('slide-left');
        setTimeout(() => { cur.style.transform = 'translateX(100%)'; prev.classList.remove('slide-left'); }, 10);
        setTimeout(() => { cur.classList.add('hidden'); cur.style.transform = 'translateX(0)'; }, 300);
        currentPage = prev.id;
    }

    function updateLine() {
        const v = document.getElementById('line_select').value;
        if (v) { const p = v.split('|'); document.getElementById('line_id').value = p[0]; document.getElementById('line_name').value = p[1]; }
    }

    function updateStation() {
        const v = document.getElementById('station_select').value;
        if (v) { const p = v.split('|'); document.getElementById('station_id').value = p[0]; document.getElementById('station_name').value = p[1]; }
    }

    async function save() {
        const data = {};
        document.querySelectorAll('input[type="text"],input[type="password"],input[type="number"],input[type="range"],input[type="hidden"],select').forEach(i => { if(i.id) data[i.id] = i.value; });
        document.querySelectorAll('input[type="checkbox"]').forEach(i => { if(i.id) data[i.id] = i.checked; });
        
        try {
            const res = await fetch('/api/save', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(data) });
            if (res.ok) { alert('Saved! Restarting...'); setTimeout(() => location.reload(), 3000); }
            else throw new Error('Save failed');
        } catch(e) { alert('Error: ' + e.message); }
    }

    window.TC = { nav, back, updateLine, updateStation, save };
})();
