// app.js - Xử lý logic toàn bộ giao diện người dùng
let currentToken = null;
let currentCandidateForDetail = null;
let funnelChartInstance = null;
let sourceChartInstance = null;
let cachedCandidates = [];
let cachedJobs = [];

// Khởi tạo ứng dụng
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    await switchUserRole('hr_linh');
    loadDashboard();
    loadJobs();
    loadCandidates();
    loadInterviews();
    loadEvaluations();
    loadSettings();
}

// 1. Chuyển đổi vai trò người dùng (Admin, HR, Interviewer)
async function switchUserRole(username) {
    try {
        const res = await fetch(`/api/auth/quick-switch/${username}`, { method: 'POST' });
        if (res.ok) {
            const data = await res.json();
            currentToken = data.access_token;
            console.log(`Đã chuyển sang vai trò: ${data.user.full_name} (${data.user.role})`);
        }
    } catch (e) {
        console.error('Lỗi chuyển vai trò:', e);
    }
}

// 2. Chuyển Tab chính
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('text-blue-600', 'bg-blue-50', 'active');
        el.classList.add('text-slate-600');
    });

    const targetTab = document.getElementById(`tab-${tabId}`);
    const targetBtn = document.getElementById(`tab-btn-${tabId}`);
    if (targetTab) targetTab.classList.add('active');
    if (targetBtn) {
        targetBtn.classList.add('text-blue-600', 'bg-blue-50', 'active');
        targetBtn.classList.remove('text-slate-600');
    }

    if (tabId === 'dashboard') loadDashboard();
    if (tabId === 'candidates') loadCandidates();
    if (tabId === 'jobs') loadJobs();
    if (tabId === 'interviews') loadInterviews();
    if (tabId === 'evaluations') loadEvaluations();
}

// 3. Tab AI Workbench: chuyển đổi sub-tabs
function switchAISubTab(subTabId) {
    document.querySelectorAll('.ai-sub-panel').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.ai-sub-btn').forEach(el => {
        el.classList.remove('text-blue-600', 'border-b-2', 'border-blue-600');
        el.classList.add('text-slate-500');
    });

    const target = document.getElementById(`ai-sub-content-${subTabId.replace('ai-', '')}`);
    const btn = document.getElementById(`ai-sub-tab-${subTabId.replace('ai-', '')}`);
    if (target) target.classList.remove('hidden');
    if (btn) {
        btn.classList.add('text-blue-600', 'border-b-2', 'border-blue-600');
        btn.classList.remove('text-slate-500');
    }
}

// 4. TỔNG QUAN & THỐNG KÊ (KPIs & Charts)
async function loadDashboard() {
    try {
        const res = await fetch('/api/statistics/dashboard');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('statTotalCandidates').innerText = data.summary.total_candidates;
        document.getElementById('statActiveJobs').innerText = data.summary.active_jobs;
        document.getElementById('statPassRate').innerText = `${data.summary.interview_pass_rate}%`;

        // Render Funnel Chart
        renderFunnelChart(data.funnel);
        // Render Source Chart
        renderSourceChart(data.sources);
    } catch (e) {
        console.error('Lỗi nạp thống kê:', e);
    }
}

function renderFunnelChart(funnel) {
    const ctx = document.getElementById('funnelChart').getContext('2d');
    if (funnelChartInstance) funnelChartInstance.destroy();

    funnelChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['1. Ứng tuyển (Applied)', '2. Sơ loại (Screening)', '3. Phỏng vấn (Interview)', '4. Đề nghị (Offered)', '5. Nhận việc (Hired)', '6. Từ chối (Rejected)'],
            datasets: [{
                label: 'Số lượng ứng viên theo giai đoạn',
                data: [funnel.applied, funnel.screening, funnel.interview, funnel.offered, funnel.hired, funnel.rejected],
                backgroundColor: [
                    '#3b82f6', '#0ea5e9', '#6366f1', '#8b5cf6', '#10b981', '#f43f5e'
                ],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 } }
            }
        }
    });
}

function renderSourceChart(sources) {
    const ctx = document.getElementById('sourceChart').getContext('2d');
    if (sourceChartInstance) sourceChartInstance.destroy();

    const labels = Object.keys(sources);
    const counts = Object.values(sources);

    sourceChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: ['#2563eb', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#64748b']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
            }
        }
    });
}

// 5. QUẢN LÝ VỊ TRÍ TUYỂN DỤNG
async function loadJobs() {
    try {
        const res = await fetch('/api/jobs');
        if (!res.ok) return;
        cachedJobs = await res.json();
        
        const container = document.getElementById('jobsContainer');
        const filterJobSelect = document.getElementById('candidateJobFilter');
        const modalJobSelect = document.getElementById('cJobId');

        // Update selects
        if (filterJobSelect) {
            filterJobSelect.innerHTML = '<option value="">Tất cả vị trí tuyển</option>';
            cachedJobs.forEach(j => {
                filterJobSelect.innerHTML += `<option value="${j.id}">${j.title}</option>`;
            });
        }
        if (modalJobSelect) {
            modalJobSelect.innerHTML = '';
            cachedJobs.forEach(j => {
                modalJobSelect.innerHTML += `<option value="${j.id}">${j.title} (${j.department})</option>`;
            });
        }

        // Render Job Cards
        container.innerHTML = cachedJobs.map(job => `
            <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition space-y-3 flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-semibold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded">${job.department}</span>
                        <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${job.status === 'Đang tuyển' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'}">${job.status}</span>
                    </div>
                    <h4 class="font-bold text-slate-900 text-base mt-2">${job.title}</h4>
                    <p class="text-xs text-slate-500 mt-1 line-clamp-2">${job.description}</p>
                    <div class="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
                        <span class="bg-slate-50 px-2 py-1 rounded border border-slate-100"><i class="fa-solid fa-money-bill-wave text-emerald-600 mr-1"></i>${job.salary_range}</span>
                        <span class="bg-slate-50 px-2 py-1 rounded border border-slate-100"><i class="fa-solid fa-briefcase text-slate-400 mr-1"></i>${job.experience_level}</span>
                    </div>
                </div>
                <div class="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                    <span class="text-slate-500"><i class="fa-solid fa-users text-blue-500 mr-1"></i><strong>${job.candidate_count || 0}</strong> ứng viên</span>
                    <button onclick="filterCandidatesByJob(${job.id})" class="text-blue-600 hover:text-blue-800 font-semibold flex items-center">
                        Xem ứng viên <i class="fa-solid fa-chevron-right ml-1 text-[10px]"></i>
                    </button>
                </div>
            </div>
        `).join('');

    } catch (e) {
        console.error('Lỗi nạp tin tuyển dụng:', e);
    }
}

function filterJobsTable() {
    const q = document.getElementById('jobSearchInput').value.toLowerCase();
    const filtered = cachedJobs.filter(j => j.title.toLowerCase().includes(q) || j.department.toLowerCase().includes(q));
    // render filtered jobs
    const container = document.getElementById('jobsContainer');
    container.innerHTML = filtered.map(job => `
        <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
            <h4 class="font-bold text-slate-900">${job.title}</h4>
            <p class="text-xs text-slate-500">${job.description}</p>
        </div>
    `).join('');
}

function openJobModal() { document.getElementById('jobModal').classList.remove('hidden'); }
function closeJobModal() { document.getElementById('jobModal').classList.add('hidden'); }

async function submitCreateJob(e) {
    e.preventDefault();
    const payload = {
        title: document.getElementById('jTitle').value,
        department: document.getElementById('jDept').value,
        salary_range: document.getElementById('jSalary').value || "Thỏa thuận",
        description: document.getElementById('jDesc').value,
        requirements: document.getElementById('jReq').value,
        status: "Đang tuyển"
    };
    try {
        const res = await fetch('/api/jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            closeJobModal();
            loadJobs();
            loadDashboard();
            alert('Đã đăng vị trí tuyển dụng mới thành công!');
        }
    } catch (e) {
        alert('Lỗi tạo vị trí tuyển dụng: ' + e);
    }
}

// 6. QUẢN LÝ HỒ SƠ ỨNG VIÊN
async function loadCandidates() {
    try {
        const search = document.getElementById('candidateSearchInput')?.value || '';
        const status = document.getElementById('candidateStatusFilter')?.value || '';
        const jobId = document.getElementById('candidateJobFilter')?.value || '';

        let url = `/api/candidates?`;
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (status) url += `status_filter=${encodeURIComponent(status)}&`;
        if (jobId) url += `job_id=${encodeURIComponent(jobId)}&`;

        const res = await fetch(url);
        if (!res.ok) return;
        cachedCandidates = await res.json();

        // Update selects in AI and Interview modals
        updateCandidateDropdowns();

        const tbody = document.getElementById('candidatesTableBody');
        if (!tbody) return;

        if (cachedCandidates.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="px-4 py-8 text-center text-slate-400">Không tìm thấy ứng viên nào phù hợp.</td></tr>`;
            return;
        }

        tbody.innerHTML = cachedCandidates.map(c => {
            const statusBadge = getStatusBadge(c.status);
            return `
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-4 py-3.5">
                        <div class="font-bold text-slate-900">${c.full_name}</div>
                        <div class="text-xs text-slate-500">${c.email} | ${c.phone}</div>
                    </td>
                    <td class="px-4 py-3.5 text-xs font-medium text-slate-700">
                        ${c.job_title || 'N/A'}
                    </td>
                    <td class="px-4 py-3.5">
                        <div class="text-xs text-slate-600 max-w-xs truncate" title="${c.skills || ''}">
                            ${c.skills ? c.skills.split(',').slice(0, 3).map(s => `<span class="bg-slate-100 px-1.5 py-0.5 rounded text-[11px] mr-1">${s.trim()}</span>`).join('') : '<span class="text-slate-400">Chưa có</span>'}
                        </div>
                    </td>
                    <td class="px-4 py-3.5 text-xs text-slate-600">
                        <span class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-700">${c.source}</span>
                    </td>
                    <td class="px-4 py-3.5">
                        ${statusBadge}
                    </td>
                    <td class="px-4 py-3.5 text-right space-x-1">
                        <button onclick="viewCandidateDetail(${c.id})" class="px-2.5 py-1 text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 rounded font-medium transition" title="Xem chi tiết CV">
                            <i class="fa-solid fa-eye mr-1"></i> Xem CV
                        </button>
                        <button onclick="directAnalyzeAI(${c.id})" class="px-2.5 py-1 text-xs bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded font-semibold transition" title="Tóm tắt CV bằng AI">
                            <i class="fa-solid fa-wand-magic-sparkles mr-1 text-indigo-600"></i> AI Lọc
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

    } catch (e) {
        console.error('Lỗi nạp ứng viên:', e);
    }
}

function getStatusBadge(status) {
    const map = {
        'APPLIED': '<span class="bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full text-xs font-semibold">1. Ứng tuyển</span>',
        'SCREENING': '<span class="bg-sky-50 text-sky-700 px-2.5 py-1 rounded-full text-xs font-semibold">2. Sơ loại CV</span>',
        'INTERVIEW': '<span class="bg-indigo-50 text-indigo-700 px-2.5 py-1 rounded-full text-xs font-semibold">3. Phỏng vấn</span>',
        'OFFERED': '<span class="bg-purple-50 text-purple-700 px-2.5 py-1 rounded-full text-xs font-semibold">4. Đề nghị (Offer)</span>',
        'HIRED': '<span class="bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full text-xs font-semibold">5. Nhận việc</span>',
        'REJECTED': '<span class="bg-rose-50 text-rose-700 px-2.5 py-1 rounded-full text-xs font-semibold">6. Từ chối</span>'
    };
    return map[status] || `<span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded text-xs">${status}</span>`;
}

function filterCandidatesByJob(jobId) {
    switchTab('candidates');
    const sel = document.getElementById('candidateJobFilter');
    if (sel) {
        sel.value = jobId;
        loadCandidates();
    }
}

function updateCandidateDropdowns() {
    const selects = [
        document.getElementById('aiQuickSelectCandidate'),
        document.getElementById('aiEmailCandidateSelect'),
        document.getElementById('ivCandidateSelect'),
        document.getElementById('evalCandidateSelect')
    ];
    selects.forEach(sel => {
        if (!sel) return;
        const currentVal = sel.value;
        sel.innerHTML = '<option value="">-- Chọn ứng viên --</option>';
        cachedCandidates.forEach(c => {
            sel.innerHTML += `<option value="${c.id}">${c.full_name} - ${c.job_title || ''} (${c.status})</option>`;
        });
        if (currentVal) sel.value = currentVal;
    });
}

function viewCandidateDetail(id) {
    const c = cachedCandidates.find(item => item.id === id);
    if (!c) return;
    currentCandidateForDetail = c;
    document.getElementById('cvModalCandidateName').innerText = c.full_name;
    document.getElementById('cvModalJobTitle').innerText = `Vị trí: ${c.job_title || 'N/A'} | Email: ${c.email} | SĐT: ${c.phone}`;
    document.getElementById('cvModalContent').innerText = c.cv_raw_text || 'Chưa có nội dung CV.';
    document.getElementById('cvModalStatusSelect').value = c.status;
    document.getElementById('cvDetailModal').classList.remove('hidden');
}

function closeCvDetailModal() {
    document.getElementById('cvDetailModal').classList.add('hidden');
}

async function updateCandidateStatusFromModal() {
    if (!currentCandidateForDetail) return;
    const newStatus = document.getElementById('cvModalStatusSelect').value;
    try {
        const res = await fetch(`/api/candidates/${currentCandidateForDetail.id}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify({ status: newStatus })
        });
        if (res.ok) {
            alert('Cập nhật trạng thái ứng viên thành công!');
            loadCandidates();
            loadDashboard();
            closeCvDetailModal();
        }
    } catch (e) {
        alert('Lỗi cập nhật: ' + e);
    }
}

function transferToAIWorkbench() {
    if (!currentCandidateForDetail) return;
    closeCvDetailModal();
    switchTab('ai-workbench');
    switchAISubTab('ai-summary');
    populateAICandidate(currentCandidateForDetail.id);
}

function directAnalyzeAI(candidateId) {
    switchTab('ai-workbench');
    switchAISubTab('ai-summary');
    populateAICandidate(candidateId);
    setTimeout(() => {
        runAISummary();
    }, 200);
}

function openAddCandidateModal() { document.getElementById('candidateModal').classList.remove('hidden'); }
function closeCandidateModal() { document.getElementById('candidateModal').classList.add('hidden'); }

async function submitCreateCandidate(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('full_name', document.getElementById('cName').value);
    formData.append('email', document.getElementById('cEmail').value);
    formData.append('phone', document.getElementById('cPhone').value);
    formData.append('applied_job_id', document.getElementById('cJobId').value);
    formData.append('source', document.getElementById('cSource').value);
    formData.append('skills', document.getElementById('cSkills').value);
    formData.append('cv_raw_text', document.getElementById('cCvText').value);

    const fileInput = document.getElementById('cFile');
    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    }

    try {
        const res = await fetch('/api/candidates/upload', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentToken}` },
            body: formData
        });
        if (res.ok) {
            closeCandidateModal();
            loadCandidates();
            loadDashboard();
            alert('Thêm hồ sơ ứng viên thành công!');
        }
    } catch (e) {
        alert('Lỗi tạo ứng viên: ' + e);
    }
}

// 7. LỊCH PHỎNG VẤN (INTERVIEWS)
async function loadInterviews() {
    try {
        const res = await fetch('/api/interviews');
        if (!res.ok) return;
        const interviews = await res.json();
        const tbody = document.getElementById('interviewsTableBody');
        if (!tbody) return;

        if (interviews.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="px-4 py-8 text-center text-slate-400">Chưa có lịch phỏng vấn nào.</td></tr>`;
            return;
        }

        tbody.innerHTML = interviews.map(iv => `
            <tr class="hover:bg-slate-50 transition">
                <td class="px-4 py-3 font-semibold text-slate-900">${iv.candidate_name || 'N/A'}<br><span class="text-xs font-normal text-slate-500">${iv.job_title || ''}</span></td>
                <td class="px-4 py-3 text-xs font-medium text-slate-700">${iv.round_name}</td>
                <td class="px-4 py-3 text-xs text-slate-600">${new Date(iv.scheduled_time).toLocaleString('vi-VN')}</td>
                <td class="px-4 py-3 text-xs text-slate-700">${iv.interviewer_name || 'Hội đồng phỏng vấn'}</td>
                <td class="px-4 py-3 text-xs text-slate-500 max-w-xs truncate">${iv.location_or_link}</td>
                <td class="px-4 py-3">
                    <span class="px-2 py-0.5 rounded text-xs font-semibold ${iv.result === 'PASSED' ? 'bg-emerald-100 text-emerald-800' : (iv.result === 'FAILED' ? 'bg-rose-100 text-rose-800' : 'bg-amber-100 text-amber-800')}">
                        ${iv.result === 'PASSED' ? 'ĐẠT' : (iv.result === 'FAILED' ? 'KHÔNG ĐẠT' : 'CHỜ DIỄN RA')}
                    </span>
                </td>
                <td class="px-4 py-3 text-right">
                    <button onclick="quickUpdateInterviewResult(${iv.id}, 'PASSED')" class="text-xs text-emerald-600 hover:text-emerald-800 font-bold mr-2">Đạt</button>
                    <button onclick="quickUpdateInterviewResult(${iv.id}, 'FAILED')" class="text-xs text-rose-600 hover:text-rose-800 font-bold">Trượt</button>
                </td>
            </tr>
        `).join('');

    } catch (e) {
        console.error('Lỗi nạp lịch phỏng vấn:', e);
    }
}

function openInterviewModal() { document.getElementById('interviewModal').classList.remove('hidden'); }
function closeInterviewModal() { document.getElementById('interviewModal').classList.add('hidden'); }

async function submitCreateInterview(e) {
    e.preventDefault();
    const candidateId = document.getElementById('ivCandidateSelect').value;
    const roundNumber = parseInt(document.getElementById('ivRoundNumber').value);
    const roundName = document.getElementById('ivRoundNumber').options[document.getElementById('ivRoundNumber').selectedIndex].text;
    const scheduledTime = document.getElementById('ivScheduledTime').value;
    const location = document.getElementById('ivLocation').value;

    try {
        const res = await fetch('/api/interviews', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify({
                candidate_id: parseInt(candidateId),
                round_number: roundNumber,
                round_name: roundName,
                scheduled_time: scheduledTime,
                location_or_link: location
            })
        });
        if (res.ok) {
            closeInterviewModal();
            loadInterviews();
            loadCandidates();
            loadDashboard();
            alert('Lên lịch phỏng vấn thành công!');
        }
    } catch (e) {
        alert('Lỗi lên lịch: ' + e);
    }
}

async function quickUpdateInterviewResult(ivId, result) {
    try {
        const res = await fetch(`/api/interviews/${ivId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify({ result: result })
        });
        if (res.ok) {
            loadInterviews();
            loadDashboard();
        }
    } catch (e) {
        console.error(e);
    }
}

// 8. ĐÁNH GIÁ ỨNG VIÊN (EVALUATIONS)
async function loadEvaluations() {
    try {
        const res = await fetch('/api/evaluations');
        if (!res.ok) return;
        const evals = await res.json();
        const container = document.getElementById('evaluationsContainer');
        if (!container) return;

        if (evals.length === 0) {
            container.innerHTML = `<div class="col-span-2 text-center py-8 text-slate-400">Chưa có phiếu đánh giá phỏng vấn nào.</div>`;
            return;
        }

        container.innerHTML = evals.map(ev => `
            <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-xs space-y-3">
                <div class="flex items-center justify-between border-b pb-2">
                    <div>
                        <h4 class="font-bold text-slate-900">${ev.candidate_name || 'Ứng viên'}</h4>
                        <p class="text-xs text-slate-500">Đánh giá bởi: <strong>${ev.evaluator_name || 'Hội đồng'}</strong> | ${new Date(ev.created_at).toLocaleDateString('vi-VN')}</p>
                    </div>
                    <div class="text-right">
                        <span class="text-xl font-black ${ev.total_score >= 8.0 ? 'text-emerald-600' : 'text-blue-600'}">${ev.total_score}</span>
                        <span class="text-xs text-slate-400">/10</span>
                    </div>
                </div>

                <div class="grid grid-cols-4 gap-2 text-center text-xs">
                    <div class="bg-slate-50 p-1.5 rounded"><span class="block text-slate-400 text-[10px]">Kỹ thuật</span><strong>${ev.technical_score}</strong></div>
                    <div class="bg-slate-50 p-1.5 rounded"><span class="block text-slate-400 text-[10px]">Mềm</span><strong>${ev.soft_skills_score}</strong></div>
                    <div class="bg-slate-50 p-1.5 rounded"><span class="block text-slate-400 text-[10px]">Thái độ</span><strong>${ev.attitude_score}</strong></div>
                    <div class="bg-slate-50 p-1.5 rounded"><span class="block text-slate-400 text-[10px]">Tiếng Anh</span><strong>${ev.language_score}</strong></div>
                </div>

                <div class="text-xs text-slate-600 space-y-1">
                    <p><strong>Điểm mạnh:</strong> ${ev.pros || 'Tốt'}</p>
                    <p><strong>Cần cải thiện:</strong> ${ev.cons || 'Không có'}</p>
                </div>

                <div class="pt-2 border-t flex items-center justify-between">
                    <span class="text-xs font-bold uppercase tracking-wider ${ev.recommendation === 'HIRE' ? 'text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded' : 'text-rose-700 bg-rose-50 px-2 py-0.5 rounded'}">
                        Đề xuất: ${ev.recommendation === 'HIRE' ? 'Tuyển dụng' : (ev.recommendation === 'REJECT' ? 'Từ chối' : 'Cân nhắc')}
                    </span>
                </div>
            </div>
        `).join('');

    } catch (e) {
        console.error('Lỗi nạp đánh giá:', e);
    }
}

function openEvaluationModal() { document.getElementById('evaluationModal').classList.remove('hidden'); }
function closeEvaluationModal() { document.getElementById('evaluationModal').classList.add('hidden'); }

async function submitCreateEvaluation(e) {
    e.preventDefault();
    const payload = {
        candidate_id: parseInt(document.getElementById('evalCandidateSelect').value),
        technical_score: parseFloat(document.getElementById('evalTech').value),
        soft_skills_score: parseFloat(document.getElementById('evalSoft').value),
        attitude_score: parseFloat(document.getElementById('evalAttitude').value),
        language_score: parseFloat(document.getElementById('evalLang').value),
        pros: document.getElementById('evalPros').value,
        cons: document.getElementById('evalCons').value,
        recommendation: document.getElementById('evalRecommendation').value
    };

    try {
        const res = await fetch('/api/evaluations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${currentToken}` },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            closeEvaluationModal();
            loadEvaluations();
            loadCandidates();
            loadDashboard();
            alert('Lưu phiếu đánh giá ứng viên thành công!');
        }
    } catch (e) {
        alert('Lỗi tạo đánh giá: ' + e);
    }
}

// 9. TRỢ LÝ AI: TÓM TẮT CV (3.2.1)
function populateAICandidate(candidateId) {
    if (!candidateId) return;
    const c = cachedCandidates.find(item => item.id == candidateId);
    if (!c) return;

    document.getElementById('aiCvText').value = c.cv_raw_text;
    const job = cachedJobs.find(j => j.id == c.applied_job_id);
    if (job) {
        document.getElementById('aiJobDescription').value = `${job.title}\nPhòng ban: ${job.department}\nYêu cầu: ${job.requirements}`;
    }

    // Gán dữ liệu cho gợi ý câu hỏi
    document.getElementById('aiQJobTitle').value = job ? job.title : '';
    document.getElementById('aiQSkills').value = c.skills || '';
}

async function runAISummary() {
    const jd = document.getElementById('aiJobDescription').value.trim();
    const cv = document.getElementById('aiCvText').value.trim();
    if (!jd || !cv) {
        alert('Vui lòng nhập cả Mô tả công việc (JD) và CV ứng viên!');
        return;
    }

    const btn = document.getElementById('btnRunAISummary');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Đang phân tích bằng AI...';
    btn.disabled = true;

    try {
        const res = await fetch('/api/ai/summarize-cv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_description: jd,
                cv_text: cv
            })
        });

        if (res.ok) {
            const data = await res.json();
            document.getElementById('aiMatchScoreBadge').innerText = `Độ phù hợp: ${data.match_score}%`;
            
            document.getElementById('aiSummaryOutput').innerHTML = `
                <div class="space-y-4">
                    <div class="bg-emerald-50/70 p-3.5 rounded-xl border border-emerald-200">
                        <h5 class="font-bold text-emerald-900 text-xs uppercase mb-2 flex items-center">
                            <i class="fa-solid fa-circle-check mr-1.5 text-emerald-600"></i>
                            Điểm Phù Hợp (Matching Points)
                        </h5>
                        <div class="text-xs text-emerald-950 whitespace-pre-wrap leading-relaxed">${data.matching_points}</div>
                    </div>

                    <div class="bg-amber-50/70 p-3.5 rounded-xl border border-amber-200">
                        <h5 class="font-bold text-amber-900 text-xs uppercase mb-2 flex items-center">
                            <i class="fa-solid fa-circle-question mr-1.5 text-amber-600"></i>
                            Điểm Cần Hỏi Thêm Trong Phỏng Vấn (Follow-up Questions)
                        </h5>
                        <div class="text-xs text-amber-950 whitespace-pre-wrap leading-relaxed">${data.questions_to_ask}</div>
                    </div>
                </div>
            `;

            // Anti-bias audit note
            const biasDiv = document.getElementById('aiBiasNotice');
            biasDiv.classList.remove('hidden');
            document.getElementById('aiBiasNoticeText').innerText = data.bias_audit_result;
        } else {
            alert('Lỗi từ AI Service!');
        }
    } catch (e) {
        alert('Lỗi: ' + e);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// 10. TRỢ LÝ AI: GỢI Ý CÂU HỎI PHỎNG VẤN (3.2.2)
async function runAIGenerateQuestions() {
    const jobTitle = document.getElementById('aiQJobTitle').value;
    const skills = document.getElementById('aiQSkills').value;

    try {
        const res = await fetch('/api/ai/generate-questions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_title: jobTitle,
                skills: skills
            })
        });

        if (res.ok) {
            const data = await res.json();
            const output = document.getElementById('aiQuestionsOutput');
            output.innerHTML = `
                <div class="bg-blue-50/60 p-4 rounded-xl border border-blue-200 text-xs space-y-2">
                    <h5 class="font-bold text-blue-900 uppercase flex items-center">
                        <i class="fa-solid fa-laptop-code text-blue-600 mr-1.5"></i>
                        1. Chuyên Môn Kỹ Thuật
                    </h5>
                    <div class="space-y-1.5 text-slate-700">
                        ${data.technical_questions.map(q => `<p class="leading-relaxed">${q}</p>`).join('')}
                    </div>
                </div>

                <div class="bg-indigo-50/60 p-4 rounded-xl border border-indigo-200 text-xs space-y-2">
                    <h5 class="font-bold text-indigo-900 uppercase flex items-center">
                        <i class="fa-solid fa-star text-indigo-600 mr-1.5"></i>
                        2. Tình Huống Thực Tế (STAR)
                    </h5>
                    <div class="space-y-1.5 text-slate-700">
                        ${data.situational_questions.map(q => `<p class="leading-relaxed">${q}</p>`).join('')}
                    </div>
                </div>

                <div class="bg-purple-50/60 p-4 rounded-xl border border-purple-200 text-xs space-y-2">
                    <h5 class="font-bold text-purple-900 uppercase flex items-center">
                        <i class="fa-solid fa-people-roof text-purple-600 mr-1.5"></i>
                        3. Văn Hóa & Thái Độ
                    </h5>
                    <div class="space-y-1.5 text-slate-700">
                        ${data.culture_fit_questions.map(q => `<p class="leading-relaxed">${q}</p>`).join('')}
                    </div>
                </div>
            `;
        }
    } catch (e) {
        alert('Lỗi gợi ý câu hỏi: ' + e);
    }
}

// 11. TRỢ LÝ AI: SINH EMAIL PHẢN HỒI (3.2.3)
async function runAIGenerateEmail() {
    const candidateId = document.getElementById('aiEmailCandidateSelect').value;
    if (!candidateId) {
        alert('Vui lòng chọn ứng viên nhận email!');
        return;
    }

    const payload = {
        candidate_id: parseInt(candidateId),
        email_type: document.getElementById('aiEmailTypeSelect').value,
        interview_time: document.getElementById('aiEmailTime').value,
        interview_location: document.getElementById('aiEmailLocation').value,
        custom_note: document.getElementById('aiEmailNote').value
    };

    try {
        const res = await fetch('/api/ai/generate-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            const data = await res.json();
            document.getElementById('emailSubjectOutput').value = data.subject;
            document.getElementById('emailContentOutput').value = data.content;
        }
    } catch (e) {
        alert('Lỗi sinh email: ' + e);
    }
}

function copyEmailToClipboard() {
    const subject = document.getElementById('emailSubjectOutput').value;
    const body = document.getElementById('emailContentOutput').value;
    navigator.clipboard.writeText(`Tiêu đề: ${subject}\n\n${body}`);
    alert('Đã sao chép nội dung email vào bộ nhớ tạm (Clipboard)!');
}

// 12. KIỂM THỬ THIÊN LỆCH (ANTI-BIAS BENCHMARK)
async function runBiasTest() {
    const text = document.getElementById('biasTestInput').value;
    try {
        const res = await fetch('/api/ai/test-bias', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ test_cv_text: text, attribute_to_test: 'demographics' })
        });
        if (res.ok) {
            const data = await res.json();
            document.getElementById('biasTestResult').innerHTML = `
                <div class="space-y-2">
                    <div class="flex items-center space-x-2">
                        <span class="bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded text-xs">TRẠNG THÁI: ${data.status}</span>
                        <span class="text-slate-600 font-semibold">Phát hiện: ${data.attribute_detected}</span>
                    </div>
                    <p class="text-slate-700 leading-relaxed font-medium">${data.explanation}</p>
                    <div class="bg-white p-2.5 rounded border border-slate-200 text-[11px] text-slate-500">
                        <strong>Cơ chế trung lập:</strong> ${data.neutral_evaluation}
                    </div>
                </div>
            `;
        }
    } catch (e) {
        alert('Lỗi kiểm tra thiên lệch: ' + e);
    }
}

// 13. CẤU HÌNH HỆ THỐNG & AI ENGINE
async function loadSettings() {
    try {
        const res = await fetch('/api/settings');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('configAiProvider').value = data.ai_provider;
        }
    } catch (e) {
        console.error(e);
    }
}

async function saveAISettings() {
    const geminiKey = document.getElementById('configGeminiKey').value;
    const provider = document.getElementById('configAiProvider').value;

    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                gemini_api_key: geminiKey,
                ai_provider: provider
            })
        });
        if (res.ok) {
            document.getElementById('saveSettingsMsg').innerText = 'Đã lưu cấu hình thành công!';
            setTimeout(() => { document.getElementById('saveSettingsMsg').innerText = ''; }, 3000);
        }
    } catch (e) {
        alert('Lỗi lưu: ' + e);
    }
}

async function testGeminiConnection() {
    const key = document.getElementById('configGeminiKey').value;
    if (!key) {
        alert('Vui lòng nhập API Key để kiểm tra!');
        return;
    }
    try {
        const res = await fetch('/api/settings/test-gemini-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: key })
        });
        const data = await res.json();
        alert(data.message);
    } catch (e) {
        alert('Lỗi kết nối: ' + e);
    }
}
