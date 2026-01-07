const API_BASE = '/api/v1';

const elements = {
    homeView: document.getElementById('homeView'),
    detailView: document.getElementById('detailView'),
    portfolioView: document.getElementById('portfolioView'),

    // Home Elements
    kospiPrice: document.getElementById('homeKospiPrice'),
    kospiChange: document.getElementById('homeKospiChange'),
    kosdaqPrice: document.getElementById('homeKosdaqPrice'),
    kosdaqChange: document.getElementById('homeKosdaqChange'),
    kospi200Price: document.getElementById('homeKospi200Price'),
    kospi200Change: document.getElementById('homeKospi200Change'),
    transactionRankingList: document.getElementById('transactionRankingList'),

    // Detail Elements
    stockName: document.getElementById('hogaStockName'),
    stockCodeLabel: document.getElementById('stockCodeLabel'),
    mainPrice: document.getElementById('mainCurrentPrice'),
    mainChange: document.getElementById('mainPriceChange'),
    stockSearch: document.getElementById('stockSearch'),
    hogaList: document.getElementById('hogaList'),
    stockMainChart: document.getElementById('stockMainChart'),
    orderPrice: document.getElementById('orderPrice'),
    orderQty: document.getElementById('orderQty'),
    estimatedAmount: document.getElementById('estimatedAmount'),
    buyingPower: document.getElementById('buyingPower'),
    executeOrderBtn: document.getElementById('executeOrderBtn'),

    // Portfolio Elements
    totalEvalAmount: document.getElementById('totalEvalAmount'),
    totalPflsAmount: document.getElementById('totalPflsAmount'),
    totalPflsRate: document.getElementById('totalPflsRate'),
    cashBalance: document.getElementById('cashBalance'),
    holdingsList: document.getElementById('holdingsList'),

    // Modal Elements
    modal: document.getElementById('globalModal'),
    modalTitle: document.getElementById('modalTitle'),
    modalMessage: document.getElementById('modalMessage'),
    modalCancelBtn: document.getElementById('modalCancelBtn'),
    modalConfirmBtn: document.getElementById('modalConfirmBtn'),
};

let currentOrderType = 'buy';
let currentOrderDvsn = '00'; // 00: Limit, 01: Market
let currentStockCode = '';
let currentStockPrice = 0;
let hogaInterval = null;
let homeInterval = null;
let portfolioInterval = null;

// Initialize
async function init() {
    setupEventListeners();
    window.addEventListener('popstate', handleRouting);
    handleRouting();
}

async function handleRouting() {
    const path = window.location.pathname;
    const stockMatch = path.match(/^\/stock\/(\d{6})$/);

    if (path === '/portfolio') {
        showPortfolio(false);
    } else if (stockMatch) {
        const code = stockMatch[1];
        selectStock(code, false);
    } else {
        showHome(false);
    }
}

function setupEventListeners() {
    elements.stockSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = e.target.value.trim();
            if (query) selectStock(query);
        }
    });

    document.querySelectorAll('.order-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.order-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentOrderType = tab.dataset.type;
            updateOrderUI();
        });
    });

    document.querySelectorAll('.price-type-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.price-type-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentOrderDvsn = tab.dataset.divsn;

            // If Market, disable price input
            if (currentOrderDvsn === '01') {
                elements.orderPrice.value = currentStockPrice;
                elements.orderPrice.disabled = true;
                elements.orderPrice.style.opacity = '0.5';
            } else {
                elements.orderPrice.disabled = false;
                elements.orderPrice.style.opacity = '1';
            }
            updateEstimatedAmount();
        });
    });

    elements.orderPrice.addEventListener('input', updateEstimatedAmount);
    elements.orderQty.addEventListener('input', updateEstimatedAmount);
    elements.executeOrderBtn.addEventListener('click', executeOrder);
}

async function loadHomeData() {
    // Parallel fetch for snappy responsiveness
    await Promise.all([
        fetchMarketIndices(),
        fetchTransactionRankings()
    ]);

    // "초당 거래건수 초과 (EGW00201)" 에러 방지를 위해 순차적으로 호출
    await fetchAndDrawChart('0001', 'kospiChart');
    await fetchAndDrawChart('1001', 'kosdaqChart');
    await fetchAndDrawChart('2001', 'kospi200Chart');
}

async function fetchMarketIndices() {
    try {
        const res = await fetch(`${API_BASE}/indices`);
        const data = await res.json();

        updateIndexUI('kospi', data.kospi);
        updateIndexUI('kosdaq', data.kosdaq);
        updateIndexUI('kospi200', data.kospi200);
    } catch (e) { }
}

function updateIndexUI(id, data) {
    if (!data) return;
    const priceEl = document.getElementById(`home${id.charAt(0).toUpperCase() + id.slice(1)}Price`);
    const changeEl = document.getElementById(`home${id.charAt(0).toUpperCase() + id.slice(1)}Change`);

    if (priceEl) priceEl.textContent = formatNumber(data.price);
    if (changeEl) {
        const isUp = data.change >= 0;
        changeEl.textContent = `${isUp ? '+' : ''}${formatNumber(data.change)} (${isUp ? '+' : ''}${data.rate}%)`;
        changeEl.className = `idx-change ${isUp ? 'up' : 'down'}`;
    }
}

async function fetchAndDrawChart(code, canvasId) {
    try {
        const res = await fetch(`${API_BASE}/index-chart/${code}`);
        const data = await res.json();
        // Only render if we have data to avoid clearing the last good chart
        if (data && data.length > 0) {
            renderMiniChart(canvasId, data);
        }
    } catch (e) { }
}

function renderMiniChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth * 2;
    const height = canvas.height = canvas.offsetHeight * 2;
    ctx.scale(2, 2);

    const prices = data.map(d => d.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min || 1;

    const cw = canvas.offsetWidth;
    const ch = canvas.offsetHeight;

    ctx.clearRect(0, 0, cw, ch);
    ctx.beginPath();
    ctx.lineWidth = 2;
    const isUp = prices[prices.length - 1] >= prices[0];
    ctx.strokeStyle = isUp ? '#F04452' : '#3182F6';

    data.forEach((d, i) => {
        const x = (i / (data.length - 1)) * cw;
        const y = ch - ((d.price - min) / range) * ch;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Area gradient
    ctx.lineTo(cw, ch);
    ctx.lineTo(0, ch);
    ctx.closePath();
    const grad = ctx.createLinearGradient(0, 0, 0, ch);
    grad.addColorStop(0, isUp ? 'rgba(240, 68, 82, 0.2)' : 'rgba(49, 130, 246, 0.2)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = grad;
    ctx.fill();
}

async function fetchTransactionRankings() {
    try {
        const res = await fetch(`${API_BASE}/transaction-rankings`);
        const data = await res.json();
        renderRankings(data);

        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');

        document.getElementById('lastUpdateTime').textContent = `${year}-${month}-${day} ${hours}:${minutes}:${seconds} 업데이트`;
    } catch (e) { }
}

function renderRankings(stocks) {
    if (!stocks || stocks.length === 0) return; // Keep existing items if no new ones
    elements.transactionRankingList.innerHTML = stocks.map((s, i) => `
        <div class="ranking-item" onclick="selectStock('${s.code}')">
            <div class="rank-left">
                <span class="rank-num">${i + 1}</span>
                <div class="stock-info-main">
                    <span class="stock-name">${s.name}</span>
                    <span class="stock-amount">거래대금 ${formatAmount(s.amount)}</span>
                </div>
            </div>
            <div class="rank-right">
                <span class="rank-price">${formatNumber(s.price)}원</span>
                <span class="rank-rate ${s.change_rate >= 0 ? 'up' : 'down'}">
                    ${s.change_rate >= 0 ? '+' : ''}${s.change_rate}%
                </span>
            </div>
        </div>
    `).join('');
}

async function selectStock(query, pushState = true) {
    let code = query;

    // 만약 한글명(삼성전자 등)이 입력된 경우 검색 API로 코드 조회
    if (!(query.length === 6 && /^\d+$/.test(query))) {
        try {
            const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}`);
            const results = await res.json();
            if (results && results.length > 0) {
                code = results[0].code; // 첫 번째 검색 결과 사용
            } else {
                alert('해당 종목을 찾을 수 없습니다.');
                return;
            }
        } catch (e) {
            console.error('Search failed:', e);
            return;
        }
    }

    currentStockCode = code;
    showDetail(pushState); // showDetail will clear homeInterval

    if (hogaInterval) clearInterval(hogaInterval);

    // Initial fetch for the stock details
    fetchStockData(code);

    // REAL-TIME: 2 seconds polling for detail view
    hogaInterval = setInterval(() => {
        fetchStockData(code);
    }, 2000);
}

// Helper to bundle detail fetches
async function fetchStockData(code) {
    await Promise.all([
        fetchStockDetail(code),
        fetchStockChart(code),
        fetchHoga(code),
        fetchBalance()
    ]);
}

async function fetchStockDetail(code) {
    try {
        const response = await fetch(`${API_BASE}/stock/${code}`);
        const data = await response.json();

        currentStockPrice = data.price;
        elements.stockName.textContent = data.name;
        elements.stockCodeLabel.textContent = data.code;
        elements.mainPrice.textContent = formatNumber(data.price);

        const isUp = data.change_amount >= 0;
        elements.mainPrice.className = `current-price ${isUp ? 'up' : 'down'}`;
        elements.mainChange.textContent = `${isUp ? '+' : ''}${formatNumber(data.change_amount)} (${data.change_rate}%)`;
        elements.mainChange.className = `price-change ${isUp ? 'up' : 'down'}`;

        elements.orderPrice.value = data.price;
        updateEstimatedAmount();
    } catch (e) { }
}

async function fetchHoga(code) {
    try {
        const response = await fetch(`${API_BASE}/stock/${code}/hoga`);
        const data = await response.json();
        renderHoga(data);
    } catch (e) { }
}

async function fetchStockChart(code) {
    try {
        const response = await fetch(`${API_BASE}/stock/${code}/chart`);
        const data = await response.json();
        if (data && data.length > 0) {
            renderStockChart('stockMainChart', data);
        }
    } catch (e) { }
}

function renderHoga(data) {
    const asks = (data.asks || []).reverse();
    const bids = (data.bids || []);
    const maxVol = Math.max(...[...asks, ...bids].map(x => x.volume), 1);

    let html = '';

    // Asks (Blue)
    asks.forEach(a => {
        const volPercent = (a.volume / maxVol) * 100;
        html += `
            <div class="hoga-item" onclick="setOrderPrice(${a.price})">
                <div class="hoga-vol-bar ask" style="width: ${volPercent}%"></div>
                <div class="hoga-val vol-left">${formatNumber(a.volume)}</div>
                <div class="hoga-price-cell down">${formatNumber(a.price)}</div>
                <div class="hoga-val"></div>
            </div>
        `;
    });

    // Bids (Red)
    bids.forEach(b => {
        const volPercent = (b.volume / maxVol) * 100;
        const isCurrent = b.price === currentStockPrice;
        html += `
            <div class="hoga-item ${isCurrent ? 'current' : ''}" onclick="setOrderPrice(${b.price})">
                <div class="hoga-vol-bar bid" style="width: ${volPercent}%"></div>
                <div class="hoga-val"></div>
                <div class="hoga-price-cell up">${formatNumber(b.price)}</div>
                <div class="hoga-val vol-right">${formatNumber(b.volume)}</div>
            </div>
        `;
    });

    elements.hogaList.innerHTML = html;
}

function renderStockChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !data || data.length === 0) return;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const prices = data.map(d => d.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min || 1;
    const padding = 20;
    const ch = h - padding * 2;
    const cw = w - padding * 2;

    const isUp = data[data.length - 1].price >= data[0].price;
    const color = isUp ? '#F04452' : '#3182F6';

    ctx.clearRect(0, 0, w, h);

    // Grid lines (simplified)
    ctx.strokeStyle = '#212326';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i <= 4; i++) {
        const gy = padding + (i / 4) * ch;
        ctx.moveTo(padding, gy);
        ctx.lineTo(w - padding, gy);
    }
    ctx.stroke();

    // Main line
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.lineJoin = 'round';

    data.forEach((d, i) => {
        const x = padding + (i / (data.length - 1)) * cw;
        const y = padding + ch - ((d.price - min) / range) * ch;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Fill area
    ctx.lineTo(padding + cw, padding + ch);
    ctx.lineTo(padding, padding + ch);
    ctx.closePath();
    const grad = ctx.createLinearGradient(0, padding, 0, padding + ch);
    grad.addColorStop(0, isUp ? 'rgba(240, 68, 82, 0.15)' : 'rgba(49, 130, 246, 0.15)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = grad;
    ctx.fill();

    // Only show current price marker on the right if wanted, but keep it simple as requested.
    // Removing MA overlays to keep it strictly about the native price data points.
}

function renderMA(ctx, data, period, color, min, range, padding, cw, ch) {
    if (data.length < period) return;
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.setLineDash([2, 4]);

    for (let i = period - 1; i < data.length; i++) {
        let sum = 0;
        for (let j = 0; j < period; j++) sum += data[i - j].price;
        const avg = sum / period;
        const x = padding + (i / (data.length - 1)) * cw;
        const y = padding + ch - ((avg - min) / range) * ch;
        if (i === period - 1) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.setLineDash([]);
}

function showHome(pushState = true) {
    elements.homeView.style.display = 'block';
    elements.detailView.style.display = 'none';
    elements.portfolioView.style.display = 'none';
    document.body.className = 'home-mode';

    if (pushState && window.location.pathname !== '/') {
        history.pushState({ view: 'home' }, '', '/');
    }

    // Cleanup detail/portfolio polling
    if (hogaInterval) { clearInterval(hogaInterval); hogaInterval = null; }
    if (portfolioInterval) { clearInterval(portfolioInterval); portfolioInterval = null; }

    // Start home polling if not running
    if (!homeInterval) {
        loadHomeData(); // Initial load
        homeInterval = setInterval(loadHomeData, 30000);
    }
}

function showDetail(pushState = true) {
    elements.homeView.style.display = 'none';
    elements.detailView.style.display = 'block';
    elements.portfolioView.style.display = 'none';
    document.body.className = 'detail-mode';
    window.scrollTo(0, 0);

    if (pushState && currentStockCode) {
        const path = `/stock/${currentStockCode}`;
        if (window.location.pathname !== path) {
            history.pushState({ view: 'detail', code: currentStockCode }, '', path);
        }
    }

    // Stop home polling to reduce noise
    if (homeInterval) {
        clearInterval(homeInterval);
        homeInterval = null;
    }
}

window.setOrderPrice = (price) => {
    elements.orderPrice.value = price;
    updateEstimatedAmount();
};

function updateEstimatedAmount() {
    const qty = parseInt(elements.orderQty.value) || 0;
    const price = parseFloat(elements.orderPrice.value) || 0;
    elements.estimatedAmount.textContent = formatNumber(qty * price) + '원';
}

function updateOrderUI() {
    const isBuy = currentOrderType === 'buy';
    elements.executeOrderBtn.className = `execute-btn ${isBuy ? 'buy' : 'sell'}`;
    elements.executeOrderBtn.textContent = isBuy ? '구매하기' : '판매하기';

    // Update price type tabs active state
    document.querySelectorAll('.price-type-tab').forEach(tab => {
        if (tab.dataset.ordertype === currentOrderDvsn) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    // Disable price input if market order
    elements.orderPrice.disabled = currentOrderDvsn === '01';
    if (currentOrderDvsn === '01') {
        elements.orderPrice.value = ''; // Clear price for market order
    }
}

async function showPortfolio(pushState = true) {
    if (pushState) history.pushState({ view: 'portfolio' }, '', '/portfolio'); // Added view state

    document.body.className = 'portfolio-mode';
    elements.homeView.style.display = 'none';
    elements.detailView.style.display = 'none';
    elements.portfolioView.style.display = 'block';

    if (homeInterval) clearInterval(homeInterval);
    if (hogaInterval) clearInterval(hogaInterval);
    if (portfolioInterval) clearInterval(portfolioInterval);

    fetchPortfolio();
    portfolioInterval = setInterval(fetchPortfolio, 30000);
}

async function fetchPortfolio() {
    try {
        const res = await fetch(`${API_BASE}/balance`);
        const data = await res.json();
        renderPortfolio(data);
    } catch (e) { }
}

function renderPortfolio(data) {
    const summary = data.summary || {};
    const holdings = data.holdings || [];

    elements.totalEvalAmount.textContent = `${formatNumber(summary.tot_evlu_amt || 0)}원`;
    elements.totalPflsAmount.textContent = `${formatNumber(summary.evlu_pfls_smtl_amt || 0)}원`;
    elements.totalPflsRate.textContent = `${summary.evlu_pfls_smtl_amt >= 0 ? '+' : ''}${summary.evlu_pfls_smtl_amt ? ((summary.evlu_pfls_smtl_amt / summary.pchs_amt_smtl_amt) * 100).toFixed(2) : 0}%`;
    elements.cashBalance.textContent = `${formatNumber(summary.orderable_cash || summary.dnca_tot_amt || 0)}원`;

    if (holdings.length === 0) {
        elements.holdingsList.innerHTML = '<div class="empty-msg">보유 중인 종목이 없습니다.</div>';
        return;
    }

    elements.holdingsList.innerHTML = holdings.map(h => {
        const pflsRate = parseFloat(h.evlu_pfls_rt || 0);
        return `
            <div class="holding-item" onclick="selectStock('${h.pdno}')">
                <div class="holding-info">
                    <span class="holding-name">${h.prdt_name}</span>
                    <span class="holding-code">${h.pdno}</span>
                </div>
                <div class="holding-qty">${formatNumber(h.hldg_qty)}주</div>
                <div class="holding-vals">
                    <div>${formatNumber(h.evlu_amt)}원</div>
                    <div class="item-buy-price">${formatNumber(h.pchs_avg_pric)}원</div>
                </div>
                <div class="holding-rate ${pflsRate >= 0 ? 'up' : 'down'}">
                    ${pflsRate >= 0 ? '+' : ''}${pflsRate}%
                </div>
            </div>
        `;
    }).join('');
}

async function fetchBalance() {
    try {
        const res = await fetch(`${API_BASE}/balance`);
        const data = await res.json();
        const power = parseFloat(data.summary?.orderable_cash || data.summary?.dnca_tot_amt || 0);
        elements.buyingPower.textContent = formatNumber(power) + '원';
    } catch (e) { }
}

async function executeOrder() {
    const qty = parseInt(elements.orderQty.value);
    const price = parseFloat(elements.orderPrice.value);

    if (!qty || qty <= 0) return showModal({ title: '알림', message: '수량을 입력해주세요.', type: 'alert' });
    if (currentOrderDvsn === '00' && (!price || price <= 0)) return showModal({ title: '알림', message: '가격을 입력해주세요.', type: 'alert' });

    showModal({
        title: `${currentOrderType === 'buy' ? '구매' : '판매'} 확인`,
        message: `${currentStockCode} 종목을 ${qty}주 ${currentOrderType === 'buy' ? '구매' : '판매'}하시겠습니까?`,
        type: 'confirm',
        onConfirm: async () => {
            try {
                const response = await fetch(`${API_BASE}/order`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        stock_code: currentStockCode,
                        quantity: qty,
                        price: price,
                        order_type: currentOrderType,
                        order_dvsn: currentOrderDvsn
                    })
                });

                const result = await response.json();
                if (result.error) {
                    showModal({ title: '주문 실패', message: result.error, type: 'alert' });
                } else {
                    const stockName = elements.mainPrice.offsetParent ? elements.stockName.textContent : currentStockCode;
                    const sideLabel = currentOrderType === 'buy' ? '구매' : '판매';
                    const priceLabel = currentOrderDvsn === '01' ? '시장가' : `${formatNumber(price)}원`;

                    showModal({
                        title: '주문 완료',
                        message: `[${stockName}] ${qty}주 ${priceLabel} ${sideLabel} 주문이 완료되었습니다.`,
                        type: 'alert',
                        onConfirm: () => {
                            // Navigate/Refresh only after user clicks OK
                            fetchBalance();
                            if (elements.portfolioView.style.display !== 'none') {
                                fetchPortfolio();
                            } else {
                                showPortfolio();
                            }
                            // Second refresh
                            setTimeout(() => {
                                fetchBalance();
                                fetchPortfolio();
                            }, 1000);
                        }
                    });
                }
            } catch (e) {
                showModal({ title: '오류', message: '주문 처리 중 오류가 발생했습니다.', type: 'alert' });
            }
        }
    });
}

// Modal Logic
function showModal({ title, message, type = 'alert', onConfirm, onCancel }) {
    elements.modalTitle.textContent = title;
    elements.modalMessage.textContent = message;
    elements.modal.style.display = 'flex';

    // Reset buttons
    elements.modalCancelBtn.style.display = type === 'confirm' ? 'block' : 'none';
    elements.modalConfirmBtn.textContent = '확인';

    // Clear previous event listeners
    const newConfirmBtn = elements.modalConfirmBtn.cloneNode(true);
    const newCancelBtn = elements.modalCancelBtn.cloneNode(true);
    elements.modalConfirmBtn.parentNode.replaceChild(newConfirmBtn, elements.modalConfirmBtn);
    elements.modalCancelBtn.parentNode.replaceChild(newCancelBtn, elements.modalCancelBtn);
    elements.modalConfirmBtn = newConfirmBtn;
    elements.modalCancelBtn = newCancelBtn;

    elements.modalConfirmBtn.onclick = () => {
        closeModal();
        if (onConfirm) onConfirm();
    };

    elements.modalCancelBtn.onclick = () => {
        closeModal();
        if (onCancel) onCancel();
    };
}

function closeModal() {
    elements.modal.style.display = 'none';
}

function formatNumber(num) {
    if (isNaN(num) || num === undefined || num === null) return '0';
    return new Intl.NumberFormat('ko-KR').format(num);
}

function formatAmount(amt) {
    if (amt >= 100000000) return (amt / 100000000).toFixed(1) + '억';
    if (amt >= 10000) return (amt / 10000).toFixed(1) + '만';
    return formatNumber(amt);
}

init();
