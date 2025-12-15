from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class IslamicInheritance:
    def __init__(self, heirs_list):
        """
        heirs_list: قاموس يحتوي على الورثة وأعدادهم
        مثال: {'wife': 1, 'son': 2, 'daughter': 1, 'father': 1}
        """
        self.heirs = heirs_list
        self.shares = {} # لتخزين نسب كل وارث
        self._calculate_ratios()

    def _calculate_ratios(self):
        """
        هذه الدالة الداخلية تحسب النسب المئوية لكل وارث بناء على القواعد الشرعية
        """
        # 1. فحص وجود الفرع الوارث (أبناء أو أحفاد)
        has_children = ('son' in self.heirs and self.heirs['son'] > 0) or \
                       ('daughter' in self.heirs and self.heirs['daughter'] > 0)
        
        # 2. فحص وجود أصل وارث مذكر (أب)
        has_father = 'father' in self.heirs and self.heirs['father'] > 0

        current_share_sum = 0.0

        # --- حساب نصيب الزوجين ---
        if 'husband' in self.heirs:
            share = 0.25 if has_children else 0.50
            self.shares['husband'] = share
            current_share_sum += share
        
        elif 'wife' in self.heirs:
            # الزوجات يشتركن في الثمن أو الربع
            total_wife_share = 0.125 if has_children else 0.25
            self.shares['wife'] = total_wife_share / self.heirs['wife'] # تقسيم النصيب على عدد الزوجات
            current_share_sum += total_wife_share

        # --- حساب نصيب الأبوين ---
        if 'father' in self.heirs:
            # الأب يأخذ السدس فرضاً لو فيه فرع وارث، والباقي تعصيباً لو مافي
            if has_children:
                self.shares['father'] = 1/6
                current_share_sum += 1/6
            else:
                self.shares['father'] = 0 # سيأخذ الباقي لاحقاً
        
        if 'mother' in self.heirs:
            # الأم السدس لو فيه فرع وارث أو عدد من الإخوة، والثلث لو مافي
            # (للتبسيط هنا افترضنا عدم وجود جمع من الإخوة)
            share = 1/6 if has_children else 1/3
            self.shares['mother'] = share
            current_share_sum += share

        # --- حساب العصبات (الأبناء والبنات والأب عند عدم وجود أولاد) ---
        remainder = 1.0 - current_share_sum
        if remainder < 0: remainder = 0 # (العول يحتاج معالجة خاصة)

        # حالة: الأب يأخذ الباقي تعصيباً (إذا لم يكن هناك أولاد)
        if not has_children and has_father:
            self.shares['father'] = remainder
        
        # حالة: الأولاد (للذكر مثل حظ الأنثيين)
        elif has_children:
            sons_count = self.heirs.get('son', 0)
            daughters_count = self.heirs.get('daughter', 0)
            
            # عدد الأسهم: الابن بسهمين، والبنت بسهم
            total_shares_units = (sons_count * 2) + (daughters_count * 1)
            
            if total_shares_units > 0:
                unit_value = remainder / total_shares_units
                
                if sons_count > 0:
                    self.shares['son'] = unit_value * 2
                if daughters_count > 0:
                    self.shares['daughter'] = unit_value

    def get_heir_amount(self, relation, total_estate_amount):
        """
        الدالة المطلوبة: تحسب المبلغ المالي المباشر
        """
        if relation not in self.heirs:
            return 0.0
            
        if relation not in self.shares:
            return 0.0 # محجوب أو ليس له نصيب
            
        fraction = self.shares[relation]
        amount = total_estate_amount * fraction
        return round(amount, 2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    heirs_input = data.get('heirs', {})
    total_estate = float(data.get('total_estate', 0))

    # Clean up input (remove 0 counts)
    heirs = {k: int(v) for k, v in heirs_input.items() if int(v) > 0}
    
    calculator = IslamicInheritance(heirs)
    
    results = []
    total_distributed = 0
    
    # Define display names in Arabic
    display_names = {
        'husband': 'الزوج',
        'wife': 'الزوجة',
        'father': 'الأب',
        'mother': 'الأم',
        'son': 'الابن',
        'daughter': 'البنت'
    }

    for relation, count in heirs.items():
        amount = calculator.get_heir_amount(relation, total_estate)
        # If multiple heirs of same type (e.g. 2 wives), amount returned is per person? 
        # Checking the logic: 
        # self.shares['wife'] = total_wife_share / self.heirs['wife'] -> Share is per person.
        # get_heir_amount returns amount * fraction -> Amount is per person.
        
        total_for_type = amount * count
        total_distributed += total_for_type
        
        results.append({
            'relation': relation,
            'name': display_names.get(relation, relation),
            'count': count,
            'amount_per_person': amount,
            'total_amount': total_for_type,
            'share_percentage': round(calculator.shares.get(relation, 0) * 100, 2)
        })

    return jsonify({
        'results': results,
        'total_estate': total_estate,
        'total_distributed': round(total_distributed, 2)
    })

if __name__ == '__main__':
    app.run(debug=True)
