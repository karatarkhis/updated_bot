# -*- coding: utf-8 -*-

def get_valid_input(prompt, datatype=float, unit="", min_val=None, max_val=None):
    while True:
        print("➖" * 40)
        user_input = input(f"🔹 {prompt}{' (' + unit + ')' if unit else ''}: ").strip()
        try:
            value = datatype(user_input)
            if min_val is not None and value < min_val:
                print(f"❌ مقدار باید حداقل {min_val} {unit} باشد.")
                continue
            if max_val is not None and value > max_val:
                print(f"❌ مقدار باید حداکثر {max_val} {unit} باشد.")
                continue
            print("✅ مقدار معتبر دریافت شد.")
            return value
        except ValueError:
            print("❌ مقدار نامعتبر است. لطفاً فقط عدد وارد کنید.")

def get_yes_no(prompt):
    while True:
        answer = input(f"❓ {prompt} (بله/خیر): ").strip().lower()
        if answer in ["بله", "yes", "y", "آره"]:
            return True
        elif answer in ["خیر", "نه", "no", "n"]:
            return False
        else:
            print("❌ لطفاً فقط 'بله' یا 'خیر' وارد کنید.")

def to_farsi_number(number):
    en_to_fa = str.maketrans('0123456789,', '۰۱۲۳۴۵۶۷۸۹٬')
    return f"{number:,}".translate(en_to_fa)

def print_line(label, value, unit="ریال", width_label=35, width_value=25):
    print(f"{label:<{width_label}} {value:>{width_value}} {unit}")

# ✅ دریافت ورودی‌ها
nerkh_arz = get_valid_input("نرخ ارز را وارد کنید", int, "ریال", min_val=1000)
arzesh = get_valid_input("ارزش فوب کالا را وارد کنید", float, "دلار", min_val=1)
bimeh = get_valid_input("مبلغ بیمه را وارد کنید", float, "ریال", min_val=0)
keraye_haml = get_valid_input("مبلغ کرایه حمل را وارد کنید", int, "ریال", min_val=0)
makhaz = get_valid_input("ماخذ را وارد کنید", float, "درصد", min_val=0, max_val=100)

# ✅ محاسبات اصلی
fob = nerkh_arz * arzesh
cif = fob + bimeh + keraye_haml
hoghogh_vorodi = (cif * makhaz) / 100
helal_ahmar = (hoghogh_vorodi * 1) / 1000

# ✅ پسماند
has_pasmand = get_yes_no("آیا محاسبه پسماند نیاز است؟")
pasmand = (cif * 0.5) / 1000 if has_pasmand else 0

# ✅ مالیات (ثابت بدون پسماند)
vat = (cif + hoghogh_vorodi + helal_ahmar) * 0.10

# ✅ جمع کل پرداختی
total_payment = hoghogh_vorodi + helal_ahmar + vat + pasmand

# ✅ چاپ نتایج نهایی
print("\n📦 نتیجه محاسبات نهایی:")
print("➖" * 60)
print_line("🔹 ارزش سیف کالا:", to_farsi_number(round(cif)))
print_line("🔸 حقوق ورودی کالا:", to_farsi_number(round(hoghogh_vorodi)))
print_line("🩺 یک درصد هلال احمر:", to_farsi_number(round(helal_ahmar)))
if has_pasmand:
    print_line("♻️ مبلغ پسماند:", to_farsi_number(round(pasmand)))
print_line("💰 مالیات بر ارزش افزوده :", to_farsi_number(round(vat)))
print("➖" * 60)
print_line("💳 جمع کل پرداختی نهایی:", to_farsi_number(round(total_payment)))
