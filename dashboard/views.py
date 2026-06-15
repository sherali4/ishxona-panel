import hashlib
import hmac
import time
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.conf import settings
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


def _verify_telegram(data: dict) -> bool:
    check_hash = data.pop('hash', '')
    data_check = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
    secret = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
    computed = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, check_hash):
        return False
    if time.time() - int(data.get('auth_date', 0)) > 86400:
        return False
    return True


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


def telegram_auth(request):
    data = dict(request.GET)
    data = {k: v[0] for k, v in data.items()}
    if not _verify_telegram(dict(data)):
        messages.error(request, "Telegram autentifikatsiya xatosi")
        return redirect('/login/')
    tg_id = int(data.get('id', 0))
    User = get_user_model()
    username = f"tg_{tg_id}"
    is_admin = tg_id in settings.ADMIN_IDS
    user, created = User.objects.get_or_create(username=username, defaults={
        'first_name': data.get('first_name', ''),
        'last_name': data.get('last_name', ''),
        'is_staff': is_admin,
        'is_superuser': is_admin,
    })
    if not created and is_admin and not user.is_staff:
        user.is_staff = True
        user.is_superuser = True
        user.save()
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        User = get_user_model()
        if not username or not password:
            messages.error(request, "Barcha maydonlarni to'ldiring")
        elif password != password2:
            messages.error(request, "Parollar mos kelmadi")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Bu login allaqachon band")
        elif len(password) < 6:
            messages.error(request, "Parol kamida 6 ta belgidan iborat bo'lsin")
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, f"'{username}' admini yaratildi")
            return redirect('/register/')
    User = get_user_model()
    admins = User.objects.all().values('username', 'date_joined', 'last_login')
    return render(request, 'register.html', {'admins': admins})


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
def hisobotlar_list(request):
    hisobotlar = db.get_all_hisobotlar()
    return render(request, 'hisobotlar.html', {'hisobotlar': hisobotlar})


@login_required
def bot_toggle(request):
    if request.method == 'POST':
        active = request.POST.get('active') == '1'
        db.set_bot_active(active)
        messages.success(request, "Bot holati yangilandi")
    return redirect('/')
