# SELF-HEALING FOUNDATION — AI Defense System

> **Status:** Draft v0.2 (Phase 3.5)
> **Last Updated:** 2026-10-20
> **Owner:** misterchaiproject-ops

---

## 1. Scope & Purpose

هدف هذه الوثيقة: تحديد المعمارية الدفاعية لنظام الإصلاح الذاتي (Self-Healing) داخل AI Defense System.

### 1.1 المبادئ الأساسية

- **Fail-Closed دائماً**: عند أي غموض، نرفض الإصلاح بدل التخمين.
- **Dry-Run قبل التنفيذ**: لا تعديل صامت — كل إصلاح يمر عبر Git Diff Preview.
- **Bounded Scope**: نطاق محدود بدقة (L1/L2 الآن، L3/L4 لاحقاً).
- **Zero-Regressions**: كل إصلاح يمر عبر make check (7 خطوات) + Coverage >= 80%.
- **Resource/Data Governance first**: لا يتم تفعيل Self-Healing runtime capabilities قبل وجود حدود قابلة للإنفاذ للموارد والبيانات والتنفيذ.

### 1.2 خارج النطاق (Out of Scope)

- إصلاح المنطق البرمجي (Logic Errors).
- تعديل خوارزميات التشفير (HMAC, AES-GCM).
- تعديل الـ API العام لأي وحدة أمنية.
- إصلاح فشل اختبارات (AssertionError) — يحتاج بشرياً.
- تجاوز Resource/Data/Execution Governance.

---

## 2. Architectural Levels (L1–L4)

| المستوى | الاسم | النطاق | الحالة |
|:---:|:---|:---|:---:|
| **L1** | Auto-Format | whitespace, imports, line endings | موجود (ruff format) |
| **L2** | Auto-Lint & Fix | deterministic patterns (UP038, F401, I001) | موجود (ruff check --fix) |
| **L3** | Auto-Test & Retry | cache rebuild + retry on intermittent failures | Phase 3.5 |
| **L4** | Auto-Recover & Rollback | runtime fallback + state rollback | Phase 4 |

---

## 3. Constitutional Constraints

### 3.1 Dry-Run & Diff Preview First

- لا إصلاح صامت: أي أداة Self-Healing يجب أن:
  1. تكتب التعديلات في staging مؤقت (tmp copy).
  2. تُولّد git diff من staging إلى working.
  3. تُلزم المستخدم بالمراجعة قبل التطبيق.
- استثناء: fix.sh (L1+L2) يُطبّق مباشرة لأنه deterministic + مُثبت باختبارات المشروع.

### 3.2 Bounded Scope

نمط الإصلاحات المسموح بها:

| مسموح (L1/L2) | ممنوع (يحتاج بشرياً) |
|:---|:---|
| (int, float) إلى int | تغيير قيم ثوابت أمنية |
| ترتيب imports | تعديل توقيع دالة |
| إزالة whitespace زائد | إضافة/حذف معامل |
| إزالة متغيرات غير مستخدمة | تعديل منطق if/else |
| تفكيك أسطر طويلة | تعديل رسائل Exception |

### 3.3 Fail-Closed Safety Net

قاعدة صارمة: إذا تعذّر تصنيف الخطأ بنسبة 100%، يجب على الأداة:

1. التوقف الفوري (no partial fix).
2. رفع HealingError مع السياق الكامل.
3. طباعة REJECTED: <reason> على stderr.
4. exit 1.

### 3.4 Zero-Regressions Gate

كل إصلاح (يدوي أو آلي) يجب أن يمر عبر:

```
fix -> make check (7/7) -> coverage >= 80% -> safe-commit.sh
```

أي فشل = rollback فوري من .bak أو git restore.

### 3.5 Resource/Data/Execution Governance Gate

قبل أي L3/L4 runtime healing capability، يجب أن تتوفر وتُختبر الحدود المعرفة في:

`docs/RESOURCE_DATA_GOVERNANCE.md`

وتشمل على الأقل: resource budgets, data classification/retention, execution authorization, isolation, circuit breakers, audit evidence, verification, and rollback.

Prompt instructions are not considered an enforcement boundary.

---

## 4. Diagnostic Utility: make doctor

### 4.1 الهدف

أداة تشخيص البيئة قبل أي إصلاح ذاتي. تكشف 5 فئات من المشاكل:

| # | الفحص | الأمر |
|:---:|:---|:---|
| 1 | إصدار Python (3.12.3) | python --version |
| 2 | مزامنة uv.lock | uv lock --check |
| 3 | سلامة pre-commit cache | pre-commit run --all-files |
| 4 | تنظيف caches | find + rm |
| 5 | ملفات .bak يتيمة | find -name *.bak |

### 4.2 الواجهة

```
make doctor          # تشخيص شامل
make doctor --fix    # تشخيص + إصلاح cache فقط (آمن)
```

### 4.3 المخرجات المتوقعة

```
=== AI Defense System: Environment Doctor ===

[1/5] Python version....... OK (3.12.3)
[2/5] uv.lock sync......... OK
[3/5] pre-commit cache..... OK
[4/5] pytest cache......... STALE (will clean with --fix)
[5/5] orphaned .bak files.. NONE

SUMMARY: 4 OK, 1 STALE, 0 ERRORS
Run 'make doctor --fix' to clean stale caches.
```

---

## 5. Execution Flow

```
[Developer Edit]
    |
[pre-commit hook] -- (fail) --> [Human intervention]
    | (pass)
[make doctor] -- (unhealthy) --> [Auto-fix cache / Stop]
    | (healthy)
[make check] -- (fail) --> [Diagnose + Stop (Fail-Closed)]
    | (7/7 pass + coverage >= 80%)
[safe-commit.sh] -- (pass) --> [push to origin/main]
```

### 5.1 Human Gates الإلزامية

| الحالة | التدخل البشري مطلوب؟ |
|:---|:---:|
| فشل mypy --strict | نعم |
| فشل اختبار (AssertionError) | نعم |
| فشل bandit (تحذير أمني) | نعم |
| فشل pip-audit (CVE) | نعم |
| تعديل على src/audit/ أو src/channel/ | نعم |
| تنسيق imports (I001) | لا (auto-fix) |
| whitespace زائد | لا (auto-fix) |
| UP038 (PEP 604) | لا (auto-fix) |

---

## 6. Integration with Existing Tooling

| الأداة | العلاقة بـ Self-Healing |
|:---|:---|
| fix.sh | يُنفّذ L1 + L2 (auto-format + auto-lint) |
| check.sh | يُفعّل Zero-Regressions Gate |
| safe-commit.sh | يُغلِف كل شيء في commit ذرّي |
| pre-commit | Gate أخير قبل git |
| Makefile | نقطة دخول موحّدة (make doctor) |
| Resource/Data Governance | يحدد حدود الموارد والبيانات والتنفيذ قبل L3/L4 |

---

## 7. Future Work (Phase 4+)

| المرحلة | الميزة | التعقيد |
|:---:|:---|:---:|
| **3.5** | make doctor + safe-commit.sh --files | منخفض |
| **4** | L3 (Auto-Test Retry) + Runtime Circuit Breaker | متوسط |
| **5** | L4 (Auto-Rollback) + SIEM Integration | عالٍ |
| **6** | LLM-Assisted Repair | عالٍ جداً |

### 7.1 LLM-Assisted Repair (Vision)

- Error Analysis Prompt: يمرّر Traceback + مقتطف الكود المُصاب فقط.
- Targeted Fix Prompt: يُلزم النموذج بإخراج patch محدود النطاق.
- Constraint: النموذج لا يُنفّذ — يقتصر على اقتراح patch يمر عبر Human Gate.
- **Additional constraint:** LLM output can propose an action, but deterministic contracts/policies decide whether that action is executable.

---

## 8. Threat Model Coverage

| التهديد | التخفيف |
|:---|:---|
| إصلاح خاطئ (False Positive) | Dry-Run + Bounded Scope + Fail-Closed |
| كسر منطق أمني | Human Gate على src/audit/ و src/channel/ |
| انحدار صامت | Zero-Regressions Gate + Coverage Gate |
| دَين تقني تراكمي | make doctor دوري + cache cleanup |
| Prompt Injection على LLM Repair | Bounded Scope + Human Approval + deterministic enforcement |
| Resource exhaustion | Resource budgets + rate/concurrency limits + circuit breakers |
| Data leakage | identity-bound authorization + classification + retention + isolation |
| Self-Healing privilege escalation | allowlisted actions + immutable capability boundary |

---

## 9. References

- `docs/RESOURCE_DATA_GOVERNANCE.md` — Resource, Data & Execution Governance baseline
- docs/THREAT_MODEL.md — §15 (Known Gaps)
- docs/CONSTITUTION.md — §3 (Forbidden Patterns)
- docs/VERIFICATION_PROTOCOL.md — Pre-Flight Checklist
- docs/MASTER_PLAN.md — Roadmap
