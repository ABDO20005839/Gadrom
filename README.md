# 🍗 Bazooka Chicken – Real-time Restaurant System

## التشغيل

```bash
pip install flask flask-socketio
python app.py
```

ثم افتح:
- **المنيو (للعميل):** http://localhost:5000/
- **لوحة الكاشير:** http://localhost:5000/cashtarhar

## بيانات الدخول (الكاشير)
| المستخدم | كلمة المرور |
|----------|------------|
| escor    | 80         |
| escor    | 90         |

## الميزات
- ✅ طلب مباشر بدون تحديث الصفحة (Socket.IO)
- 🔔 جرس تنبيه عند وصول طلب جديد للكاشير
- 📊 إحصائيات حية (انتظار / تحضير / سُلِّم / إيرادات)
- 🔄 تحديث حالة الطلب (انتظار ← تحضير ← سُلِّم)
- 🗑 حذف الطلبات
- 💾 حفظ الطلبات في ملف JSON

## هيكل الملفات
```
restaurant/
├── app.py                    # Flask + Socket.IO
├── requirements.txt
├── orders.json               # يُنشأ تلقائياً
└── templates/
    ├── index.html            # صفحة العميل
    ├── cashier_login.html    # تسجيل دخول الكاشير
    └── cashier_dashboard.html # لوحة الكاشير
```
