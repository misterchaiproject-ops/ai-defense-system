# THREAT MODEL — AI Defense System

> **Status:** Draft v0.1 (Phase 2.5)
> **Last Updated:** 2026-10-03
> **Owner:** misterchaiproject-ops

---

## 1. Scope & Purpose

هذه الوثيقة تُحدّد نموذج التهديدات (Threat Model) الرسمي لمشروع AI Defense System. هدفها:

- توثيق الأصول التي نحميها.
- تحديد حدود الثقة (Trust Boundaries) بين المكونات.
- سرد متجهات الهجوم المحتملة.
- إثبات الضوابط الحالية (Mitigations).
- الإفصاح عن الفجوات المُعترف بها.
- وضع خطة معالجة زمنية.

خارج النطاق:
- البنية التحتية للاستضافة (Codespaces, GitHub).
- أمن شبكة النقل (TLS يُوفّرها GitHub).
- أمن الأجهزة الفيزيائية (Samsung Tab S9).

---

## 2. Assets - الأصول الحساسة

| الأصل | الوصف | الحساسية |
|:---|:---|:---:|
| shared_secret | مفتاح HMAC المشترك بين الوكلاء | CRITICAL |
| AgentIdentity | هوية الوكيل + أدواره | HIGH |
| Proposal | الطلب المُوقّع | HIGH |
| Envelope | الرسالة المُوقّعة | HIGH |
| Guardrail rules | قواعد الأمان (الحدود) | HIGH |
| _ReplayCache | ذاكرة الـ nonces المستخدمة | MEDIUM |
| audit.log | سجل العمليات | MEDIUM |

---

## 3. Trust Boundaries - حدود الثقة

النظام يحتوي على 3 حدود ثقة:

### 3.1 الحدود الخارجية (External -> Channel)
- المدخل: Envelope من وكيل خارجي.
- الفحص: التوقيع، الطابع الزمني، الـ nonce.
- المخرج: قبول (للـ Orchestrator) أو رفض (Fail-Closed).

### 3.2 الحدود الداخلية (Channel -> Orchestrator)
- المدخل: Envelope مُتحقَّق منه.
- الفحص: إعادة بناء Proposal + Guardrail.
- المخرج: ValidationResult (قبول/رفض).

### 3.3 حدود السياسة (Orchestrator -> Guardrail)
- المدخل: Proposal + AgentIdentity.
- الفحص: الحدود الفيزيائية (limits/min_values).
- المخرج: ValidationResult مُلزم.

---

## 4. Attack Vectors - متجهات الهجوم

### 4.1 Forgery - التزوير

| # | الهجوم | التأثير المحتمل |
|:---:|:---|:---|
| F1 | تزوير التوقيع (Signature Forgery) | وكيل مُنتحل يُرسل أوامر خبيثة |
| F2 | سرقة الـ shared_secret | السيطرة الكاملة على القناة |
| F3 | رسالة تحمل key_id مختلف (Key-ID Confusion) | خلط المفاتيح بين الوكلاء |
| F4 | Replay Attack (إعادة إرسال رسالة قديمة) | تنفيذ أمر بشكل مكرر |

### 4.2 Injection - الحقن

| # | الهجوم | التأثير المحتمل |
|:---:|:---|:---|
| I1 | Indirect Prompt Injection | حقن أوامر خبيثة في payload |
| I2 | Control Character Injection | كسر التحقق النصي |
| I3 | Unicode Homoglyph Attack | استخدام أحرف متشابهة للتحايل |
| I4 | JSON Deserialization Attack | كسر المُحلّل عبر بنية JSON معقدة |

### 4.3 Privilege Escalation - تصعيد الصلاحيات

| # | الهجوم | التأثير المحتمل |
|:---:|:---|:---|
| P1 | Role Spoofing | انتحال دور ADMIN |
| P2 | Tool-Call Hijacking | استدعاء أدوات غير مصرّح بها |
| P3 | Guardrail Bypass | تجاوز الحدود الفيزيائية |

### 4.4 Denial of Service - إيقاف الخدمة

| # | الهجوم | التأثير المحتمل |
|:---:|:---|:---|
| D1 | Oversized Payload | استهلاك الذاكرة |
| D2 | Nonce Flooding | امتلاء _ReplayCache |
| D3 | Timestamp Manipulation | تعطيل التحقق الزمني |

---

## 5. Mitigations - آليات التصدي

### 5.1 ضد التزوير (F1-F4)

| الهجوم | الضابط | الموقع في الكود |
|:---|:---|:---|
| F1 | HMAC-SHA256 مع compare_digest | `channel.core.verify_message` |
| F2 | 32-byte secret إلزامي + تحقق الطول | `channel.core.__post_init__` |
| F3 | فحص key_id بـ regex صارم | `channel.core._SENDER_RE` |
| F4 | _ReplayCache مع nonce + timestamp | `channel.core._ReplayCache` |

### 5.2 ضد الحقن (I1-I4)

| الهجوم | الضابط | الموقع في الكود |
|:---|:---|:---|
| I1 | Guardrail إلزامي قبل التنفيذ | `orchestrator.core.process_inbound` |
| I2 | regex يرفض control chars | `contracts.proposal._CONTROL_CHARS` |
| I3 | ASCII-only في JSON canonicalization | `channel.core._canonicalize` |
| I4 | json.loads مع رفض غير المتوقع | `contracts.proposal._reconstruct` |

### 5.3 ضد تصعيد الصلاحيات (P1-P3)

| الهجوم | الضابط | الموقع في الكود |
|:---|:---|:---|
| P1 | AgentIdentity مع frozenset(Role) | `contracts.agent_identity` |
| P2 | لا توجد أداة تنفيذ مباشر (Data-only) | Architecture decision |
| P3 | Guardrail لا يمكن تجاوزه (fail-closed) | `orchestrator.core.process_outbound` |

### 5.4 ضد إيقاف الخدمة (D1-D3)

| الهجوم | الضابط | الموقع في الكود |
|:---|:---|:---|
| D1 | _MAX_PAYLOAD_BYTES (limit صريح) | `channel.core._canonicalize` |
| D2 | _ReplayCache بـ TTL محدود | `channel.core._ReplayCache` |
| D3 | التحقق من timestamp مع نافذة ±300s | `channel.core.verify_message` |

### 5.5 مبادئ عامة

1. **Fail-Closed:** أي استثناء غير متوقع -> رفض (not allow).
2. **No Silent Failures:** كل رفض يُسجّل في audit.log.
3. **Defense in Depth:** 3 طبقات (Channel -> Reconstruct -> Guardrail).
4. **Immutable Contracts:** كل dataclass هو `frozen=True, slots=True`.
5. **Type Safety:** mypy --strict على كل ملفات src/.

---

## 6. Known Gaps - الفجوات المُعترف بها

نُفصح بشفافية عن الفجوات الحالية، مع تحديد الأولوية:

| # | الفجوة | المخاطرة | الأولوية |
|:---:|:---|:---:|:---:|
| G1 | _ReplayCache غير دائم (In-Memory) - يُفقد عند إعادة التشغيل | إعادة تشغيل الخدمة تفتح نافذة Replay | HIGH |
| G2 | No key rotation mechanism - المفتاح ثابت | تسرب المفتاح = اختراق دائم | HIGH |
| G3 | No Multi-Agent trust graph (كل الوكلاء يثقون بنفس القناة) | وكيل مخترق يمكنه التحدث مع آخرين | MEDIUM |
| G4 | Guardrail قواعده ثابتة (لا Adaptive policies) | لا يستجيب لتهديدات جديدة | MEDIUM |
| G5 | audit.log غير مُشفّر (قد يحتوي معلومات حساسة) | تسرب معلومات في حالة اختراق النظام | MEDIUM |
| G6 | No rate limiting على مستوى الوكيل | وكيل مخترق يمكنه إغراق النظام | LOW |
| G7 | No SIEM integration (لا يوجد ربط مع أنظمة مراقبة) | صعوبة اكتشاف الهجمات في الوقت الحقيقي | LOW |

---

## 7. Roadmap - خطة المعالجة

### Phase 3 (قريباً)
- **G1:** تحويل _ReplayCache إلى Redis/File-based.
- **G2:** تنفيذ key rotation يدوي (مع دعم مفتاحين نشطين).
- **G5:** تشفير audit.log (AES-256).

### Phase 4 (متوسط المدى)
- **G3:** إضافة Multi-Agent trust graph.
- **G4:** Guardrail مع policies قابلة للتحديث.
- **G6:** Rate limiting per agent_id.

### Phase 5+ (طويل المدى)
- **G7:** ربط مع SIEM (مثل Prometheus + Grafana).
- إضافة Anomaly Detection (ML-based).
- Compliance مع معايير (ISO 27001, NIST).

---

## 8. Review & Maintenance

- **Review Cycle:** كل 3 أشهر (أو عند تغيير معماري كبير).
- **Owner:** misterchaiproject-ops.
- **Approval:** Self-reviewed (Phase 2.5). سيُطلب مراجعة خارجية في Phase 6+.
- **Related Documents:**
  - `docs/CONSTITUTION.md` - المبادئ الستة.
  - `docs/VERIFICATION_PROTOCOL.md` - طرق التحقق.
  - `docs/PROMPT_TEMPLATE.md` - قواعد التطوير.

---

## 9. Change Log

| التاريخ | الإصدار | التغيير |
|:---|:---:|:---|
| 2026-10-03 | v0.1 | Draft أولي (Phase 2.5) |

---

**نهاية الوثيقة.**
