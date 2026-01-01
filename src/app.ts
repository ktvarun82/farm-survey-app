/**
 * Farm Survey Application - Main TypeScript Application
 * Master-Detail View Architecture
 */

import type { FarmSurvey, FarmSurveyCreate, ApiError, Tree, TreeCreate } from './types';

const API_BASE_URL = '';

// Views
const viewList = document.getElementById('view-list') as HTMLDivElement;
const viewDetail = document.getElementById('view-detail') as HTMLDivElement;
const viewForm = document.getElementById('view-form') as HTMLDivElement;

// DOM Elements
const surveysList = document.getElementById('surveys-list') as HTMLDivElement;
const loading = document.getElementById('loading') as HTMLDivElement;
const noSurveys = document.getElementById('no-surveys') as HTMLDivElement;
const refreshBtn = document.getElementById('refresh-btn') as HTMLButtonElement;
const surveyForm = document.getElementById('survey-form') as HTMLFormElement;
const formTitle = document.getElementById('form-title') as HTMLHeadingElement;
const surveyIdInput = document.getElementById('survey-id') as HTMLInputElement;
const searchInput = document.getElementById('search-input') as HTMLInputElement;

let editingSurvey: FarmSurvey | null = null;
let currentDetailId: number | null = null; // Store for client-side filtering
let allSurveys: FarmSurvey[] = []; // Store for client-side filtering

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSurveys();

    if (surveyForm) {
        surveyForm.addEventListener('submit', handleFormSubmit);
    }

    if (refreshBtn) refreshBtn.addEventListener('click', loadSurveys);

    // Bind Search
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            filterSurveys(searchInput.value);
        });
    }

    // Initialize UI
    const syncBtn = document.getElementById('sync-btn');
    if (syncBtn) {
        syncBtn.addEventListener('click', (e) => {
            e.preventDefault();
            SyncManager.sync();
        });
    }

    SyncManager.updateUI();
});

// Register Service Worker - Disabled for now to prevent caching issues
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function (registrations) {
        for (let registration of registrations) {
            registration.unregister();
        }
    });
}

// ---------------------------------------------------------
// VIEW NAVIGATION
// ---------------------------------------------------------
function showView(viewName: 'list' | 'detail' | 'form') {
    if (viewList) viewList.style.display = viewName === 'list' ? 'block' : 'none';
    if (viewDetail) viewDetail.style.display = viewName === 'detail' ? 'block' : 'none';
    if (viewForm) viewForm.style.display = viewName === 'form' ? 'block' : 'none';
    window.scrollTo(0, 0);
}

function showListView() {
    // Clear search when going back to list? Optional. Let's keep it for now.
    // if(searchInput) searchInput.value = '';
    // renderSurveys(allSurveys);
    showView('list');
    loadSurveys(); // Refresh list to update any changes
}

function showCreateForm() {
    resetForm();
    showView('form');
}

// ---------------------------------------------------------
// DATA LOADING (LIST)
// ---------------------------------------------------------
async function loadSurveys(): Promise<void> {
    try {
        if (loading) loading.style.display = 'block';
        if (noSurveys) noSurveys.style.display = 'none';

        // Don't clear list immediately if we want smooth transition, but fine for now

        const response = await fetch(`${API_BASE_URL}/surveys/`);
        if (!response.ok) throw new Error(`Failed to fetch surveys: ${response.statusText}`);

        allSurveys = await response.json(); // Store in global variable

        if (loading) loading.style.display = 'none';

        // Apply current SEARCH filter if exists
        if (searchInput && searchInput.value.trim()) {
            filterSurveys(searchInput.value);
        } else {
            renderSurveys(allSurveys);
        }

    } catch (error) {
        if (loading) loading.style.display = 'none';
        showError(`Failed to load surveys`);
    }
}

function renderSurveys(surveysToRender: FarmSurvey[]) {
    if (!surveysList) return;
    surveysList.innerHTML = '';

    if (surveysToRender.length === 0) {
        if (noSurveys) noSurveys.style.display = 'block';
        if (allSurveys.length > 0) {
            // If we have data but filtered result is empty
            if (noSurveys) noSurveys.innerHTML = '<p>No matching surveys found.</p>';
        } else {
            if (noSurveys) noSurveys.innerHTML = '<p>No surveys found.</p>';
        }
        return;
    }

    if (noSurveys) noSurveys.style.display = 'none';

    for (const survey of surveysToRender) {
        const card = createSurveySummaryCard(survey);
        surveysList.appendChild(card);
    }
}

function filterSurveys(query: string) {
    if (!query) {
        renderSurveys(allSurveys);
        return;
    }

    const lowerQuery = query.toLowerCase();
    const filtered = allSurveys.filter(s =>
        s.farmer_name.toLowerCase().includes(lowerQuery) ||
        s.crop_type.toLowerCase().includes(lowerQuery) ||
        s.geo_location.latitude.toString().includes(lowerQuery) ||
        s.geo_location.longitude.toString().includes(lowerQuery) ||
        (s.trees && s.trees.some(t => t.species_name.toLowerCase().includes(lowerQuery)))
    );

    renderSurveys(filtered);
}


function createSurveySummaryCard(survey: FarmSurvey): HTMLDivElement {
    const card = document.createElement('div');
    card.className = 'survey-card';
    const initials = survey.farmer_name.charAt(0).toUpperCase();

    // Simple Summary click -> viewSurvey
    card.innerHTML = `
        <div style="display: flex; align-items: center;">
            <div class="card-icon" style="
                width: 40px; height: 40px; border-radius: 50%; 
                background: #E3F2FD; color: #1976D2; 
                display: flex; align-items: center; justify-content: center; 
                font-weight: bold; margin-right: 16px;">
                ${initials}
            </div>
            <div>
                <div class="card-title" style="font-weight:bold; font-size:1.1em;">${escapeHtml(survey.farmer_name)}</div>
                <div class="card-subtitle" style="color:#666;">${escapeHtml(survey.crop_type)}</div>
            </div>
            <div style="margin-left: auto;">
                <span class="material-icons" style="color:#ccc;">chevron_right</span>
            </div>
        </div>
    `;
    card.onclick = () => viewSurvey(survey.survey_id);
    return card;
}

// ---------------------------------------------------------
// DETAIL VIEW
// ---------------------------------------------------------
async function viewSurvey(id: number) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/surveys/${id}`);
        if (!response.ok) throw new Error('Failed');
        const survey: FarmSurvey = await response.json();

        // Populate Detail View
        document.getElementById('detail-farmer')!.textContent = survey.farmer_name;
        document.getElementById('detail-crop')!.textContent = survey.crop_type;
        document.getElementById('detail-location')!.textContent = `${survey.geo_location.latitude}, ${survey.geo_location.longitude}`;

        const title = document.getElementById('detail-title');
        if (title) title.textContent = `Survey #${survey.survey_id}`;

        // Bind Actions
        const editBtn = document.getElementById('detail-edit-btn');
        const deleteBtn = document.getElementById('detail-delete-btn');

        if (editBtn) editBtn.onclick = () => editSurvey(survey.survey_id);
        if (deleteBtn) deleteBtn.onclick = () => deleteSurvey(survey.survey_id, deleteBtn as HTMLButtonElement);

        // Load Trees
        await loadTreesForDetail(survey.survey_id);

        showView('detail');
    } catch (e) {
        showError('Could not load survey details');
    }
    showLoading(false);
}

async function loadTreesForDetail(surveyId: number) {
    const container = document.getElementById('detail-trees-container');
    if (!container) return;

    container.innerHTML = '<div style="padding:10px; color:#666;">Loading trees...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/surveys/${surveyId}/trees/`);
        const trees: Tree[] = await response.json();

        const treesRows = trees.map(tree => `
            <tr>
                <td>${escapeHtml(tree.species_name)}</td>
                <td>${tree.tree_count}</td>
                <td>${tree.height_avg || '-'}</td>
                <td>${tree.diameter_avg || '-'}</td>
                <td>${tree.age_avg || '-'}</td>
                <td style="max-width: 150px; overflow: hidden; text-overflow: ellipsis;">${escapeHtml(tree.notes || '-')}</td>
                <td>
                    <button class="btn-icon-small" onclick="editTree(${tree.tree_id}, ${surveyId})" title="Edit">
                        <span class="material-icons" style="font-size: 16px;">edit</span>
                    </button>
                    <button class="btn-icon-small delete" onclick="deleteTree(${tree.tree_id}, ${surveyId})" title="Delete">
                        <span class="material-icons" style="font-size: 16px;">delete</span>
                    </button>
                </td>
            </tr>
        `).join('');

        const treesTable = `
            <div class="tree-table-container">
                <table class="tree-table">
                    <thead>
                        <tr>
                            <th>Species</th>
                            <th>Count</th>
                            <th>Height (m)</th>
                            <th>Diam (cm)</th>
                            <th>Age (y)</th>
                            <th>Notes</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${treesRows}
                    </tbody>
                </table>
            </div>
            <div style="margin-top:10px; text-align:right;">
                <button class="btn-add-tree-inline" onclick="showAddTreeForm(${surveyId})">+ Add Tree</button>
            </div>
        `;

        container.innerHTML = trees.length > 0 ? treesTable : `
            <p style="font-style:italic; color:#999; padding: 10px;">No trees recorded.</p>
            <div style="text-align:right;">
                <button class="btn-add-tree-inline" onclick="showAddTreeForm(${surveyId})">+ Add First Tree</button>
            </div>
        `;

    } catch (e) {
        container.innerHTML = 'Error loading trees.';
    }
}

// ---------------------------------------------------------
// FORM & ACTIONS
// ---------------------------------------------------------
async function editSurvey(id: number) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/surveys/${id}`);
        const survey: FarmSurvey = await response.json();
        editingSurvey = survey;

        // Populate Form
        if (surveyIdInput) surveyIdInput.value = survey.survey_id.toString();
        (document.getElementById('farmer-name') as HTMLInputElement).value = survey.farmer_name;
        (document.getElementById('crop-type') as HTMLInputElement).value = survey.crop_type;
        (document.getElementById('latitude') as HTMLInputElement).value = survey.geo_location.latitude.toString();
        (document.getElementById('longitude') as HTMLInputElement).value = survey.geo_location.longitude.toString();
        (document.getElementById('sync-status') as HTMLInputElement).checked = survey.sync_status;

        formTitle.textContent = 'Edit Survey';
        showView('form');
    } catch (e) {
        showError('Failed to load for editing');
    }
    showLoading(false);
}

async function handleFormSubmit(e: Event) {
    e.preventDefault();
    const surveyData: FarmSurveyCreate = {
        farmer_name: (document.getElementById('farmer-name') as HTMLInputElement).value,
        crop_type: (document.getElementById('crop-type') as HTMLInputElement).value,
        geo_location: {
            latitude: parseFloat((document.getElementById('latitude') as HTMLInputElement).value),
            longitude: parseFloat((document.getElementById('longitude') as HTMLInputElement).value)
        },
        sync_status: (document.getElementById('sync-status') as HTMLInputElement).checked
    };

    try {
        if (editingSurvey) {
            const lastUpdatedParam = encodeURIComponent(editingSurvey.last_updated);
            const response = await fetch(`${API_BASE_URL}/surveys/${editingSurvey.survey_id}?last_updated=${lastUpdatedParam}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(surveyData)
            });
            if (!response.ok) {
                if (response.status === 409) showError('Conflict: Modified elsewhere.');
                else throw new Error('Update failed');
                return;
            }
            showSuccess('Updated!');
            viewSurvey(editingSurvey.survey_id); // Return to Detail View
        } else {
            const response = await fetch(`${API_BASE_URL}/surveys/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(surveyData)
            });
            if (!response.ok) throw new Error('Create failed');
            showSuccess('Created!');
            showListView(); // Return to List
        }
    } catch (e) {
        showError('Operation failed');
    }
}

async function deleteSurvey(id: number, btnElement?: HTMLButtonElement) {
    const btn = btnElement || document.querySelector(`button[onclick="deleteSurvey(${id})"]`) as HTMLButtonElement;
    if (btn) {
        if (btn.getAttribute('data-confirm') !== 'true') {
            const originalText = btn.innerHTML;
            btn.innerHTML = 'Confirm?';
            btn.style.backgroundColor = 'red';
            btn.setAttribute('data-confirm', 'true');
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.backgroundColor = '';
                btn.removeAttribute('data-confirm');
            }, 3000);
            return;
        }
    }

    try {
        const response = await fetch(`${API_BASE_URL}/surveys/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Delete failed');
        showSuccess('Deleted');
        showListView();
    } catch (e) {
        showError('Delete failed');
    }
}

function resetForm() {
    if (surveyForm) surveyForm.reset();
    editingSurvey = null;
    formTitle.textContent = 'Create New Survey';
}

// ---------------------------------------------------------
// TREE POPUPS (Add/Edit)
// ---------------------------------------------------------
function showAddTreeForm(surveyId: number): void {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Add Tree</h3>
            <form id="tree-form-${surveyId}">
                <!-- Same Form Fields as before -->
                <div class="form-group"><label>Species Name *</label><input type="text" id="tree-species-${surveyId}" required></div>
                <div class="form-group"><label>Tree Count *</label><input type="number" id="tree-count-${surveyId}" min="1" required></div>
                <div class="form-group-row">
                    <div class="form-group"><label>Height (m)</label><input type="number" id="tree-height-${surveyId}" step="0.1" min="0"></div>
                    <div class="form-group"><label>Diameter (cm)</label><input type="number" id="tree-diameter-${surveyId}" step="0.1" min="0"></div>
                </div>
                <div class="form-group"><label>Age (years)</label><input type="number" id="tree-age-${surveyId}" min="0"></div>
                <div class="form-group"><label>Notes</label><textarea id="tree-notes-${surveyId}" rows="3"></textarea></div>
                <div class="form-actions">
                    <button type="submit">Add Tree</button>
                    <button type="button" class="btn-cancel" onclick="this.closest('.modal').remove()">Cancel</button>
                </div>
            </form>
        </div>
    `;
    document.body.appendChild(modal);
    const form = modal.querySelector(`#tree-form-${surveyId}`) as HTMLFormElement;
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleTreeSubmit(surveyId, null, modal);
    });
}

async function editTree(treeId: number, surveyId: number) {
    try {
        const response = await fetch(`${API_BASE_URL}/trees/${treeId}`);
        if (!response.ok) throw new Error('Failed to fetch tree');
        const tree: Tree = await response.json();

        const modal = document.createElement('div');
        modal.className = 'modal';
        // (Simplified for brevity in Artifact, assuming fields exist like before)
        modal.innerHTML = `
            <div class="modal-content">
                <h3>Edit Tree</h3>
                <form id="tree-form-${treeId}">
                    <div class="form-group"><label>Species Name *</label><input type="text" id="tree-species-${treeId}" value="${escapeHtml(tree.species_name)}" required></div>
                    <div class="form-group"><label>Tree Count *</label><input type="number" id="tree-count-${treeId}" value="${tree.tree_count}" min="1" required></div>
                    <div class="form-group-row">
                        <div class="form-group"><label>Height (m)</label><input type="number" id="tree-height-${treeId}" value="${tree.height_avg || ''}" step="0.1" min="0"></div>
                        <div class="form-group"><label>Diameter (cm)</label><input type="number" id="tree-diameter-${treeId}" value="${tree.diameter_avg || ''}" step="0.1" min="0"></div>
                    </div>
                    <div class="form-group"><label>Age (years)</label><input type="number" id="tree-age-${treeId}" value="${tree.age_avg || ''}" min="0"></div>
                    <div class="form-group"><label>Notes</label><textarea id="tree-notes-${treeId}" rows="3">${escapeHtml(tree.notes || '')}</textarea></div>
                    <div class="form-actions">
                        <button type="submit">Update Tree</button>
                        <button type="button" class="btn-cancel" onclick="this.closest('.modal').remove()">Cancel</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);
        const form = modal.querySelector(`#tree-form-${treeId}`) as HTMLFormElement;
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleTreeSubmit(surveyId, treeId, modal);
        });
    } catch (e) { showError('Load failed'); }
}

async function handleTreeSubmit(surveyId: number, treeId: number | null, modal: HTMLElement) {
    try {
        const idSuffix = treeId ? treeId : surveyId;
        const treeData: TreeCreate = {
            species_name: (document.getElementById(`tree-species-${idSuffix}`) as HTMLInputElement).value,
            tree_count: parseInt((document.getElementById(`tree-count-${idSuffix}`) as HTMLInputElement).value),
            height_avg: parseFloat((document.getElementById(`tree-height-${idSuffix}`) as HTMLInputElement).value) || null,
            diameter_avg: parseFloat((document.getElementById(`tree-diameter-${idSuffix}`) as HTMLInputElement).value) || null,
            age_avg: parseInt((document.getElementById(`tree-age-${idSuffix}`) as HTMLInputElement).value) || null,
            notes: (document.getElementById(`tree-notes-${idSuffix}`) as HTMLTextAreaElement).value || null
        };

        const url = treeId ? `${API_BASE_URL}/trees/${treeId}` : `${API_BASE_URL}/surveys/${surveyId}/trees/`;
        const method = treeId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(treeData)
        });

        if (!response.ok) throw new Error('Save failed');
        showSuccess('Saved!');
        modal.remove();
        loadTreesForDetail(surveyId); // Critical: Refresh Detail View
    } catch (e) { showError('Error saving tree'); }
}

async function deleteTree(treeId: number, surveyId: number) {
    if (!confirm('Delete Tree?')) return;
    try {
        await fetch(`${API_BASE_URL}/trees/${treeId}`, { method: 'DELETE' });
        showSuccess('Deleted');
        loadTreesForDetail(surveyId);
    } catch (e) { showError('Failed delete'); }
}

// ---------------------------------------------------------
// SYNC & HELPERS
// ---------------------------------------------------------
class SyncManager {
    static updateUI() { /* ... kept simple for now ... */ }
    static async sync() { }
}

function showLoading(show: boolean) {
    if (loading) loading.style.display = show ? 'block' : 'none';
}
function showError(msg: string) { alert(msg); } // Simple alert for errors in this new view
function showSuccess(msg: string) { /* maybe a toast? Use existing logic */
    const d = document.createElement('div');
    d.className = 'success-message message';
    d.textContent = msg;
    document.body.prepend(d);
    setTimeout(() => d.remove(), 2000);
}
function escapeHtml(text: string) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

declare global {
    interface Window {
        showCreateForm: () => void;
        showListView: () => void;
        viewSurvey: (id: number) => void;
        editSurvey: (id: number) => void;
        deleteSurvey: (id: number, btn?: HTMLButtonElement) => void;
        showAddTreeForm: (id: number) => void;
        editTree: (tid: number, sid: number) => void;
        deleteTree: (tid: number, sid: number) => void;
    }
}
window.showCreateForm = showCreateForm;
window.showListView = showListView;
window.viewSurvey = viewSurvey;
window.editSurvey = editSurvey;
window.deleteSurvey = deleteSurvey;
window.showAddTreeForm = showAddTreeForm;
window.editTree = editTree;
window.deleteTree = deleteTree;
