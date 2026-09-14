// 退出登录函数
async function logoutUser() {
    if (!confirm('确定要退出登录吗？')) return;
    try {
        const res = await fetch('/auth/logout', { method: 'POST' });
        const json = await res.json();
        if (json.code === 200) {
            window.location.href = '/login';
        } else {
            alert(json.message || '退出失败');
        }
    } catch (e) {
        console.error('Logout error:', e);
        window.location.href = '/login';
    }
}

// 统一数据格式化工具
const Formatter = {
    currency: (val) => '$' + (Number(val) || 0).toFixed(2),
    number: (val) => (Number(val) || 0).toLocaleString(),
    rating: (val) => '★ ' + (Number(val) || 0).toFixed(2)
};
