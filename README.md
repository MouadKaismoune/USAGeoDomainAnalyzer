# USAGeoDomainAnalyzer

**USA Geo Domain Analyzer** — تطبيق سطح مكتب مبني بـ **Python + PySide6** يفحص توفر الدومينات جغرافياً عبر المدن الأمريكية والنيتشات المستهدفة.

## ما الذي يقدمه؟

- نافذة عصرية **بدون إطار** مع زوايا دائرية، ظل ناعم، سحب من الهيدر، وتكبير/تصغير مرن
- **Sidebar قابل للطي** مع مجموعات تنقل (رئيسية / تحليل / نظام) ومؤشر للصفحة النشطة
- **أوضاع فاتح / داكن** مع زر تبديل في الهيدر
- **8 صفحات**: لوحة التحكم، المدن، النيتشات، المحلل، الدومينات، الصيانة، النسخ الاحتياطي، معلومات التطبيق
- تحليل نطاقات `<city><niche>.com` عبر واجهة **Verisign RDAP**
- قاعدة بيانات **SQLite** مع **نسخ احتياطي واسترجاع**
- نظام ترجمة عبر ملفات **JSON**
- صفحة **Info** مع روابط تواصل (LinkedIn / GitHub / Email)

## التشغيل

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## البنية

```text
main.py               نقطة الدخول
app/
  core/               الإعدادات والأيقونات وروابط التواصل
  ui/
    components/       Header, Sidebar, Footer
    layouts/          إطار النافذة والتخطيط والنافذة الرئيسية
    navigation/       نظام التنقل (config → registry → manager)
    pages/            الصفحات (Home, Reports)
    themes/           أنظمة الألوان الفاتح/الداكن
moduls/
  cities/             إدارة المدن
  niches/             إدارة النيتشات
  analyzer/           المحلل (تحليل الدومينات)
  domains/            استكشاف الدومينات
  maintenance/        إعادة فحص الدومينات المجهولة
  backup/             النسخ الاحتياطي واسترجاع قاعدة البيانات
  info/               معلومات التطبيق والتواصل
database/             SQLite (models + manager + app_data.db)
translator/           ملفات الترجمة JSON
widgets.py            عناصر جداول قابلة للفرز
config/               إعدادات محفوظة (اللغة، الثيم، حجم النافذة)
assets/icons/         أيقونات SVG
```

## صفحة التحليل

تتبع مبدأ `ui.py → controller.py → services.py → database/models.py`، ويعمل التحليل الجماعي عبر خيط `QThread` مع إخراج حي للنتائج.

## الترخيص

هذا المشروع مرخّص بموجب [رخصة MIT](LICENSE). حقوق النشر © 2026 Mouad Kaismoune.