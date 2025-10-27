// 慕班策思 - 前端应用逻辑

const API_BASE = window.location.origin;
let currentUser = null;
let authToken = null;
let currentChatSession = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initEventListeners();
});

// 检查认证状态
function checkAuth() {
    authToken = localStorage.getItem('authToken');
    if (authToken) {
        fetch(`${API_BASE}/api/auth/me`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        })
        .then(res => res.json())
        .then(user => {
            currentUser = user;
            showPage('dashboard');
            loadStructures();
        })
        .catch(() => {
            localStorage.removeItem('authToken');
            showPage('login');
        });
    } else {
        showPage('login');
    }
}

// 初始化事件监听
function initEventListeners() {
    // 登录表单
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        showLoading(true);
        try {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await fetch(`${API_BASE}/api/auth/login`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                authToken = data.access_token;
                currentUser = data.user;
                localStorage.setItem('authToken', authToken);
                showToast('登录成功！', 'success');
                showPage('dashboard');
                loadStructures();
            } else {
                const error = await response.json();
                showToast(error.detail || '登录失败', 'error');
            }
        } catch (error) {
            showToast('网络错误', 'error');
        } finally {
            showLoading(false);
        }
    });

    // 注册表单
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;

        showLoading(true);
        try {
            const response = await fetch(`${API_BASE}/api/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            if (response.ok) {
                const data = await response.json();
                authToken = data.access_token;
                currentUser = data.user;
                localStorage.setItem('authToken', authToken);
                showToast('注册成功！', 'success');
                showPage('dashboard');
                loadStructures();
            } else {
                const error = await response.json();
                showToast(error.detail || '注册失败', 'error');
            }
        } catch (error) {
            showToast('网络错误', 'error');
        } finally {
            showLoading(false);
        }
    });

    // 聊天输入框回车发送
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// 切换认证标签
function switchAuthTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    if (tab === 'login') {
        document.getElementById('loginForm').style.display = 'flex';
        document.getElementById('registerForm').style.display = 'none';
    } else {
        document.getElementById('loginForm').style.display = 'none';
        document.getElementById('registerForm').style.display = 'flex';
    }
}

// 显示页面
function showPage(pageName) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // 显示目标页面
    const targetPage = document.getElementById(`${pageName}Page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }

    // 显示或隐藏导航栏
    const navbar = document.getElementById('navbar');
    if (pageName === 'login') {
        navbar.style.display = 'none';
    } else {
        navbar.style.display = 'block';
    }

    // 根据页面加载数据
    if (pageName === 'history') {
        loadHistory();
    } else if (pageName === 'generate') {
        loadStructures();
    }
}

// 退出登录
function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    showPage('login');
    showToast('已退出登录', 'info');
}

// 发送聊天消息
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();

    if (!message) return;

    const model = document.getElementById('chatModel').value;

    // 显示用户消息
    addChatMessage('user', message);
    input.value = '';

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                session_id: currentChatSession,
                message: message,
                ai_model: model
            })
        });

        if (response.ok) {
            const data = await response.json();
            currentChatSession = data.session_id;
            addChatMessage('assistant', data.message.content);

            // 如果有建议，显示保存按钮
            if (data.suggestions && data.suggestions.length > 0) {
                addSaveStructureButton();
            }
        } else {
            showToast('发送失败', 'error');
        }
    } catch (error) {
        showToast('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 添加聊天消息到界面
function addChatMessage(role, content) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = content.replace(/\n/g, '<br>');

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 添加保存结构按钮
function addSaveStructureButton() {
    const messagesContainer = document.getElementById('chatMessages');
    const buttonDiv = document.createElement('div');
    buttonDiv.className = 'chat-message assistant';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `
        <p>看起来你已经确定了结构！</p>
        <button class="btn btn-primary" onclick="saveStructureFromChat()">
            <i class="fas fa-save"></i> 保存为模板
        </button>
    `;

    buttonDiv.appendChild(contentDiv);
    messagesContainer.appendChild(buttonDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// 从对话保存结构
async function saveStructureFromChat() {
    if (!currentChatSession) {
        showToast('没有活动的对话会话', 'error');
        return;
    }

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/chat/sessions/${currentChatSession}/save-structure`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const structure = await response.json();
            showToast('结构已保存！', 'success');
            addChatMessage('assistant', `✅ 结构"${structure.name}"已成功保存为模板！现在你可以在"生成内容"页面使用它了。`);
            loadStructures(); // 重新加载结构列表
        } else {
            showToast('保存失败', 'error');
        }
    } catch (error) {
        showToast('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 加载内容结构列表
async function loadStructures() {
    try {
        const response = await fetch(`${API_BASE}/api/content/structures`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const structures = await response.json();
            const select = document.getElementById('structureSelect');
            select.innerHTML = '';

            if (structures.length === 0) {
                select.innerHTML = '<option value="">暂无模板，请先在AI对话中创建</option>';
            } else {
                structures.forEach(structure => {
                    const option = document.createElement('option');
                    option.value = structure.id;
                    option.textContent = structure.name + (structure.is_default ? ' (默认)' : '');
                    select.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('加载结构失败', error);
    }
}

// 搜索热点话题
async function searchHotTopics() {
    const keyword = document.getElementById('generateKeyword').value.trim();

    if (!keyword) {
        showToast('请输入搜索关键词', 'error');
        return;
    }

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/content/search-hot`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                keyword: keyword,
                max_results: 10
            })
        });

        if (response.ok) {
            const data = await response.json();
            displayHotTopics(data.topics);
            showToast(`找到 ${data.total} 条热点`, 'success');
        } else {
            showToast('搜索失败', 'error');
        }
    } catch (error) {
        showToast('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 显示热点话题
function displayHotTopics(topics) {
    const container = document.getElementById('hotTopicsList');
    container.innerHTML = '';

    topics.forEach(topic => {
        const topicDiv = document.createElement('div');
        topicDiv.className = 'history-item';
        topicDiv.innerHTML = `
            <h4><i class="fas fa-fire"></i> ${topic.platform} - ${topic.title}</h4>
            <p>${topic.content || '暂无描述'}</p>
            <small>热度: ${topic.hot_score || 'N/A'}</small>
        `;
        container.appendChild(topicDiv);
    });

    document.getElementById('hotTopicsResult').style.display = 'block';
}

// 生成内容
async function generateContent() {
    const keyword = document.getElementById('generateKeyword').value.trim();
    const structureId = document.getElementById('structureSelect').value;
    const model = document.getElementById('generateModel').value;

    // 获取选中的平台
    const platformCheckboxes = document.querySelectorAll('#platformSelector input[type="checkbox"]:checked');
    const targetPlatforms = Array.from(platformCheckboxes).map(cb => cb.value);

    if (!keyword) {
        showToast('请输入关键词', 'error');
        return;
    }

    if (!structureId) {
        showToast('请选择内容结构', 'error');
        return;
    }

    if (targetPlatforms.length === 0) {
        showToast('请至少选择一个目标平台', 'error');
        return;
    }

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/content/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                keyword: keyword,
                structure_id: parseInt(structureId),
                target_platforms: targetPlatforms,
                ai_model: model
            })
        });

        if (response.ok) {
            const data = await response.json();
            displayGeneratedContent(data);
            showToast('内容生成成功！', 'success');
        } else {
            const error = await response.json();
            showToast(error.detail || '生成失败', 'error');
        }
    } catch (error) {
        showToast('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 显示生成的内容
function displayGeneratedContent(data) {
    const container = document.getElementById('generatedContent');
    container.innerHTML = '';

    // 显示原始内容
    const originalDiv = document.createElement('div');
    originalDiv.innerHTML = '<h4><i class="fas fa-file-alt"></i> 原始内容</h4>';
    for (const [key, value] of Object.entries(data.generated_content)) {
        originalDiv.innerHTML += `<p><strong>${key}:</strong> ${value}</p>`;
    }
    container.appendChild(originalDiv);

    // 显示各平台适配版本
    if (data.platform_adaptations) {
        const platformsDiv = document.createElement('div');
        platformsDiv.innerHTML = '<h4 style="margin-top: 2rem;"><i class="fas fa-globe"></i> 平台适配版本</h4>';

        for (const [platform, adaptation] of Object.entries(data.platform_adaptations)) {
            const platformDiv = document.createElement('div');
            platformDiv.style.marginTop = '1rem';
            platformDiv.style.padding = '1rem';
            platformDiv.style.background = '#f7fafc';
            platformDiv.style.borderRadius = '8px';
            platformDiv.innerHTML = `
                <h5>${adaptation.platform_name} (${adaptation.length}字)</h5>
                <p style="white-space: pre-wrap;">${adaptation.content}</p>
                <button class="btn btn-secondary" onclick="copyToClipboard('${platform}')">
                    <i class="fas fa-copy"></i> 复制
                </button>
            `;
            platformsDiv.appendChild(platformDiv);
        }

        container.appendChild(platformsDiv);
    }

    document.getElementById('generateResult').style.display = 'block';

    // 滚动到结果
    document.getElementById('generateResult').scrollIntoView({ behavior: 'smooth' });
}

// 复制到剪贴板
function copyToClipboard(platform) {
    // 这里需要获取具体内容，简化处理
    showToast('已复制到剪贴板', 'success');
}

// 加载历史记录
async function loadHistory() {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/content/history?page=1&page_size=20`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            displayHistory(data.items);
        } else {
            showToast('加载历史记录失败', 'error');
        }
    } catch (error) {
        showToast('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 显示历史记录
function displayHistory(items) {
    const container = document.getElementById('historyList');
    container.innerHTML = '';

    if (items.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: white;">暂无历史记录</p>';
        return;
    }

    items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'history-item';
        itemDiv.innerHTML = `
            <h4><i class="fas fa-file-alt"></i> ${item.keyword}</h4>
            <p>生成时间: ${new Date(item.created_at).toLocaleString()}</p>
            <p>AI模型: ${item.ai_model === 'openai' ? 'OpenAI GPT-4' : 'DeepSeek V3'}</p>
        `;
        itemDiv.onclick = () => viewHistoryItem(item.id);
        container.appendChild(itemDiv);
    });
}

// 查看历史记录详情
async function viewHistoryItem(id) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/api/content/history/${id}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            // 这里可以打开一个模态框显示详情
            alert('查看历史记录详情功能待实现');
        }
    } catch (error) {
        showToast('网络错误', 'error');
    } finally {
        showLoading(false);
    }
}

// 显示/隐藏加载动画
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

// 显示Toast通知
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
