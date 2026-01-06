const API_BASE = 'http://localhost:8000/api/v1';
const FAVORITE_STOCKS = ['005930', '000660', '035420', '035720', '005380']; // 삼성, SK하이닉스, 네이버, 카카오, 현대차

const elements = {
    stockList: document.getElementById('stockList'),
    orderStockCode: document.getElementById('orderStockCode'),
    orderQty: document.getElementById('orderQty'),
    estimatedAmount: document.getElementById('estimatedAmount'),
    executeOrderBtn: document.getElementById('executeOrderBtn'),
    tabs: document.querySelectorAll('.tab'),
};

let currentOrderType = 'buy';
let currentStockPrice = 0;

// Initialize
async function init() {
    setupEventListeners();
    await fetchWatchlist();
}

function setupEventListeners() {
    // Tab switching
    elements.tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            elements.tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentOrderType = tab.dataset.type;

            // UI Update for Buy/Sell
            elements.executeOrderBtn.className = `btn-order ${currentOrderType}`;
            elements.executeOrderBtn.textContent = currentOrderType === 'buy' ? '매수하기' : '매도하기';
        });
    });

    // Qty change calculation
    elements.orderQty.addEventListener('input', updateEstimatedAmount);

    // Order Button
    elements.executeOrderBtn.addEventListener('click', executeOrder);

    // Initial stock sync
    elements.orderStockCode.addEventListener('blur', () => {
        fetchStockDetail(elements.orderStockCode.value);
    });
    fetchStockDetail(elements.orderStockCode.value);
}

async function fetchWatchlist() {
    elements.stockList.innerHTML = '';

    for (const code of FAVORITE_STOCKS) {
        try {
            const response = await fetch(`${API_BASE}/stock/${code}`);
            const stock = await response.json();
            renderStockItem(stock);
        } catch (error) {
            console.error(`Failed to fetch ${code}:`, error);
        }
    }
}

function renderStockItem(stock) {
    const isPositive = stock.change_amount >= 0;
    const item = document.createElement('div');
    item.className = 'stock-item';
    item.innerHTML = `
        <div class="stock-info">
            <span class="stock-name">${stock.name}</span>
            <span class="stock-code">${stock.code}</span>
        </div>
        <div class="stock-price-box">
            <span class="stock-price">${formatNumber(stock.price)}원</span>
            <span class="stock-change ${isPositive ? 'positive' : 'negative'}">
                ${isPositive ? '▲' : '▼'} ${formatNumber(Math.abs(stock.change_amount))} (${stock.change_rate}%)
            </span>
        </div>
    `;

    item.addEventListener('click', () => {
        elements.orderStockCode.value = stock.code;
        fetchStockDetail(stock.code);
    });

    elements.stockList.appendChild(item);
}

async function fetchStockDetail(code) {
    try {
        const response = await fetch(`${API_BASE}/stock/${code}`);
        if (!response.ok) return;
        const stock = await response.json();
        currentStockPrice = stock.price;
        updateEstimatedAmount();
    } catch (error) {
        console.error('Error fetching stock detail:', error);
    }
}

function updateEstimatedAmount() {
    const qty = parseInt(elements.orderQty.value) || 0;
    const total = qty * currentStockPrice;
    elements.estimatedAmount.textContent = `${formatNumber(total)}원`;
}

async function executeOrder() {
    const code = elements.orderStockCode.value;
    const qty = parseInt(elements.orderQty.value);

    if (!code || !qty || qty <= 0) {
        alert('올바른 종목코드와 수량을 입력해주세요.');
        return;
    }

    elements.executeOrderBtn.disabled = true;
    elements.executeOrderBtn.textContent = '처리 중...';

    try {
        const response = await fetch(`${API_BASE}/order`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                stock_code: code,
                quantity: qty,
                price: currentStockPrice,
                order_type: currentOrderType
            })
        });

        const result = await response.json();

        if (response.ok) {
            alert(`${currentOrderType === 'buy' ? '매수' : '매도'} 주문이 완료되었습니다.\n주문번호: ${result.ODNO || '모의처리'}`);
        } else {
            alert(`주문에 실패했습니다: ${result.detail || result.msg1}`);
        }
    } catch (error) {
        alert('네트워크 오류가 발생했습니다.');
    } finally {
        elements.executeOrderBtn.disabled = false;
        elements.executeOrderBtn.textContent = currentOrderType === 'buy' ? '매수하기' : '매도하기';
    }
}

function formatNumber(num) {
    return new Intl.NumberFormat('ko-KR').format(num);
}

init();
