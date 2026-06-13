from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . import db

ROLES = ["user", "moderator", "vip", "hisobchi1", "hisobchi2", "otgruzkachi", "banned"]
ROLE_LABELS = {
    "user": "👤 User",
    "moderator": "🛡 Moderator",
    "vip": "⭐️ VIP",
    "hisobchi1": "🧾 Hisobchi 1",
    "hisobchi2": "🧾 Hisobchi 2",
    "otgruzkachi": "📦 Otgruzkachi",
    "banned": "🚫 Banned",
}


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('/')
        messages.error(request, "Login yoki parol noto'g'ri")
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def dashboard(request):
    users = db.get_all_users()
    korxonalar = db.get_all_korxonalar()
    bot_active = db.get_bot_active()
    role_counts = {}
    for u in users:
        for r in (u['role'] or '').split(','):
            r = r.strip()
            if r:
                role_counts[r] = role_counts.get(r, 0) + 1
    return render(request, 'dashboard.html', {
        'user_count': len(users),
        'korxona_count': len(korxonalar),
        'bot_active': bot_active,
        'role_counts': role_counts,
        'role_labels': ROLE_LABELS,
    })


@login_required
def users_list(request):
    search = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    users = db.get_all_users()
    if search:
        users = [u for u in users if search in (u['phone'] or '') or search in (u['first_name'] or '') or search == str(u['user_id'])]
    if role_filter:
        users = [u for u in users if role_filter in (u['role'] or '').split(',')]
    return render(request, 'users.html', {
        'users': users,
        'roles': ROLES,
        'role_labels': ROLE_LABELS,
        'search': search,
        'role_filter': role_filter,
    })


@login_required
def user_edit(request, user_id):
    user = db.get_user(user_id)
    if not user:
        messages.error(request, "Foydalanuvchi topilmadi")
        return redirect('/users/')
    if request.method == 'POST':
        selected = request.POST.getlist('roles')
        db.set_role(user_id, ','.join(selected))
        messages.success(request, "Rol yangilandi")
        return redirect('/users/')
    current_roles = (user['role'] or '').split(',')
    return render(request, 'user_edit.html', {
        'u': user,
        'roles': ROLES,
        'role_labels': ROLE_LABELS,
        'current_roles': current_roles,
    })


@login_required
def user_delete(request, user_id):
    if request.method == 'POST':
        db.delete_user(user_id)
        messages.success(request, "Foydalanuvchi o'chirildi")
    return redirect('/users/')


@login_required
def korxonalar_list(request):
    korxonalar = db.get_all_korxonalar()
    return render(request, 'korxonalar.html', {'korxonalar': korxonalar})


@login_required
def korxona_add(request):
    if request.method == 'POST':
        nomi = request.POST.get('nomi', '').strip()
        inn = request.POST.get('inn', '').strip()
        if not nomi or not inn:
            messages.error(request, "Nomi va INN to'ldirilishi shart")
        elif len(inn) != 9 or not inn.isdigit():
            messages.error(request, "INN 9 ta raqamdan iborat bo'lishi kerak")
        elif db.inn_exists(inn):
            messages.error(request, "Bu INN allaqachon mavjud")
        else:
            db.add_korxona(nomi, inn)
            messages.success(request, "Korxona qo'shildi")
            return redirect('/korxonalar/')
    return render(request, 'korxona_form.html', {'action': 'add'})


@login_required
def korxona_edit(request, k_id):
    korxona = db.get_korxona(k_id)
    if not korxona:
        messages.error(request, "Korxona topilmadi")
        return redirect('/korxonalar/')
    if request.method == 'POST':
        nomi = request.POST.get('nomi', '').strip()
        inn = request.POST.get('inn', '').strip()
        if not nomi or not inn:
            messages.error(request, "Nomi va INN to'ldirilishi shart")
        elif len(inn) != 9 or not inn.isdigit():
            messages.error(request, "INN 9 ta raqamdan iborat bo'lishi kerak")
        elif db.inn_exists(inn, exclude_id=k_id):
            messages.error(request, "Bu INN allaqachon mavjud")
        else:
            db.update_korxona(k_id, nomi, inn)
            messages.success(request, "Korxona yangilandi")
            return redirect('/korxonalar/')
    return render(request, 'korxona_form.html', {'action': 'edit', 'korxona': korxona})


@login_required
def korxona_delete(request, k_id):
    if request.method == 'POST':
        db.delete_korxona(k_id)
        messages.success(request, "Korxona o'chirildi")
    return redirect('/korxonalar/')


@login_required
def bot_toggle(request):
    if request.method == 'POST':
        active = request.POST.get('active') == '1'
        db.set_bot_active(active)
        messages.success(request, "Bot holati yangilandi")
    return redirect('/')
