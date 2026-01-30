// Spec Home Analyzer - Main JavaScript

// Selected properties management
let selectedProperties = [];

async function loadSelected() {
    try {
        const response = await fetch('/api/selected');
        selectedProperties = await response.json();
        updateSelectedUI();
    } catch (error) {
        console.error('Error loading selected properties:', error);
    }
}

async function getSelected() {
    try {
        const response = await fetch('/api/selected');
        return await response.json();
    } catch (error) {
        console.error('Error getting selected properties:', error);
        return [];
    }
}

async function selectProperty(property) {
    try {
        const response = await fetch('/api/selected', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(property)
        });
        selectedProperties = await response.json();
        updateSelectedUI();

        // Load comps for the selected property
        if (property.latLong && property.latLong.latitude) {
            loadCompsForProperty(property);
        }
    } catch (error) {
        console.error('Error selecting property:', error);
    }
}

async function loadCompsForProperty(property) {
    const compsPanel = document.getElementById('comps-panel');
    const compsList = document.getElementById('comps-list');

    if (!compsPanel || !compsList) return;

    compsPanel.style.display = 'block';
    compsList.innerHTML = '<div class="loading-comps">Loading nearby sales...</div>';

    try {
        const lat = property.latLong.latitude;
        const lng = property.latLong.longitude;
        const response = await fetch(`/api/comps/nearby?lat=${lat}&lng=${lng}`);
        const data = await response.json();

        if (data.success && data.results.length > 0) {
            compsList.innerHTML = `
                <div class="comps-for">
                    <strong>Comps for:</strong> ${property.address?.street || 'Selected Property'}
                </div>
                ${data.results.map(comp => {
                    const addr = comp.address || {};
                    const pricePerSqft = comp.livingArea > 0 ? Math.round(comp.unformattedPrice / comp.livingArea) : 0;
                    return `
                        <div class="comp-item">
                            <div class="comp-image">
                                <img src="${comp.imgSrc}" alt="">
                            </div>
                            <div class="comp-info">
                                <div class="comp-price">$${comp.unformattedPrice?.toLocaleString()}</div>
                                <div class="comp-ppsf">${pricePerSqft > 0 ? '$' + pricePerSqft + '/sqft' : ''}</div>
                                <div class="comp-address">${addr.street || 'N/A'}</div>
                                <div class="comp-details">
                                    ${comp.beds || '?'}bd ${comp.baths || '?'}ba · ${(comp.livingArea || 0).toLocaleString()}sqft
                                </div>
                                <div class="comp-distance">${comp.distance} mi away</div>
                            </div>
                        </div>
                    `;
                }).join('')}
            `;
        } else {
            compsList.innerHTML = '<div class="no-comps">No nearby sales found</div>';
        }
    } catch (error) {
        compsList.innerHTML = '<div class="error">Error loading comps</div>';
        console.error('Error loading comps:', error);
    }
}

async function removeSelected(propertyId) {
    try {
        const response = await fetch('/api/selected', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: propertyId })
        });
        selectedProperties = await response.json();
        updateSelectedUI();
    } catch (error) {
        console.error('Error removing property:', error);
    }
}

function updateSelectedUI() {
    // Update count in navbar
    const countEl = document.getElementById('selected-count');
    if (countEl) {
        countEl.textContent = selectedProperties.length;
    }

    // Update sidebar list
    const listEl = document.getElementById('selected-list');
    if (listEl) {
        if (selectedProperties.length === 0) {
            listEl.innerHTML = '<p style="color: #6b7280; font-size: 0.875rem;">No properties selected yet</p>';
        } else {
            listEl.innerHTML = selectedProperties.map(prop => {
                const address = prop.address || {};
                return `
                    <div class="selected-item">
                        <img src="${prop.imgSrc || '/static/img/no-image.png'}" alt="">
                        <div class="selected-item-info">
                            <div class="selected-item-price">${prop.price || '$' + prop.unformattedPrice?.toLocaleString()}</div>
                            <div class="selected-item-address">${address.street || 'Unknown'}</div>
                        </div>
                        <button class="btn btn-remove" onclick="removeSelected('${prop.id}')" title="Remove">×</button>
                    </div>
                `;
            }).join('');
        }
    }

    // Update analyze button
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
        analyzeBtn.disabled = selectedProperties.length === 0;
    }

    // Update select buttons on property cards
    updateSelectButtons();
}

function updateSelectButtons() {
    const selectedIds = selectedProperties.map(p => p.id);

    document.querySelectorAll('.property-card').forEach(card => {
        const cardId = card.dataset.id;
        const btn = card.querySelector('.btn-select');
        if (btn) {
            if (selectedIds.includes(cardId)) {
                btn.classList.add('selected');
                btn.textContent = '✓ Selected';
            } else {
                btn.classList.remove('selected');
                btn.textContent = '+ Select';
            }
        }
    });
}

function analyzeSelected() {
    window.location.href = '/analyze';
}

// Format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
    }).format(value);
}

// Format number
function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

// Toggle sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const icon = document.getElementById('sidebar-toggle-icon');
    sidebar.classList.toggle('minimized');
    document.body.classList.toggle('sidebar-minimized');
    icon.textContent = sidebar.classList.contains('minimized') ? '▶' : '◀';
}

// Auto-minimize sidebar on analyze page
if (window.location.pathname === '/analyze') {
    document.addEventListener('DOMContentLoaded', () => {
        const sidebar = document.getElementById('sidebar');
        const icon = document.getElementById('sidebar-toggle-icon');
        if (sidebar && icon) {
            sidebar.classList.add('minimized');
            document.body.classList.add('sidebar-minimized');
            icon.textContent = '▶';
        }
    });
}
