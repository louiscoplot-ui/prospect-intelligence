"""
Score Prospects — Analyse un export RPData CSV et génère prospects_data.json
Usage : python score_prospects.py <fichier_rpdata.csv> [--suburb SUBURB]
"""
import csv
import json
import sys
from datetime import datetime, date
from collections import defaultdict

def parse_price(s):
    s = s.replace('$','').replace(',','').strip()
    try: return int(s)
    except: return None

def parse_date(s):
    for fmt in ['%d %b %Y', '%d/%m/%Y']:
        try: return datetime.strptime(s.strip(), fmt).date()
        except: pass
    return None

def score_property(holding_years, prop_type, gain_pct, purchase_year):
    score = 0
    reasons = []
    
    h = holding_years
    if 5 <= h < 8:
        score += 3; reasons.append('5-8 ans de détention (zone upgrade/famille)')
    elif 8 <= h < 12:
        score += 4; reasons.append('8-12 ans de détention (peak de revente)')
    elif 12 <= h < 20:
        score += 5; reasons.append('12-20 ans de détention (profil downsizer)')
    elif 20 <= h < 30:
        score += 4; reasons.append('20-30 ans de détention (succession probable)')
    elif h >= 30:
        score += 3; reasons.append('30+ ans (succession/retraite)')
    
    if 'House' in prop_type:
        score += 1; reasons.append('Maison individuelle')
    
    if gain_pct > 200:
        score += 3; reasons.append(f'+{gain_pct}% de plus-value estimée')
    elif gain_pct > 100:
        score += 2; reasons.append(f'+{gain_pct}% de plus-value estimée')
    elif gain_pct > 50:
        score += 1; reasons.append(f'+{gain_pct}% de plus-value estimée')
    
    if 2010 <= purchase_year <= 2016:
        score += 1; reasons.append('Acheté pendant creux Perth 2010-2016')

    if h >= 15:
        profile = 'Downsizer probable'
    elif h >= 8:
        profile = 'Upgrade / changement de vie'
    elif h >= 5:
        profile = 'Investisseur ou rotation'
    else:
        profile = 'Trop récent'

    return score, reasons, profile

def main():
    if len(sys.argv) < 2:
        print("Usage: python score_prospects.py <fichier_rpdata.csv>")
        sys.exit(1)

    csv_file = sys.argv[1]
    cagr = 0.07  # Cottesloe long-term CAGR
    today = date.today()

    data = []
    with open(csv_file, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)

    props = defaultdict(list)
    for row in data:
        if len(row) < 13: continue
        addr_key = (row[0].strip(), row[1].strip(), row[3].strip())
        sale_date = parse_date(row[12])
        sale_price = parse_price(row[11])
        if sale_date and sale_price:
            props[addr_key].append({
                'address': row[0].strip(),
                'suburb': row[1].strip(),
                'postcode': row[3].strip(),
                'prop_type': row[4].strip(),
                'beds': row[5].strip(),
                'baths': row[6].strip(),
                'land_size': row[8].strip(),
                'sale_price': sale_price,
                'sale_date': sale_date,
                'agency': row[14].strip() if len(row) > 14 else '',
                'agent': row[15].strip() if len(row) > 15 else '',
                'owner1': row[19].strip() if len(row) > 19 else '',
                'owner2': row[20].strip() if len(row) > 20 else '',
            })

    result = []
    for addr_key, sales in props.items():
        sales_sorted = sorted(sales, key=lambda x: x['sale_date'])
        latest = sales_sorted[-1]
        purchase_date = latest['sale_date']
        holding_years = round((today - purchase_date).days / 365.25, 1)
        earliest = sales_sorted[0]
        
        years_since = (today - earliest['sale_date']).days / 365.25
        estimated_value = int(earliest['sale_price'] * (1 + cagr) ** years_since)
        gain_estimate = estimated_value - latest['sale_price']
        gain_pct = round((gain_estimate / latest['sale_price']) * 100) if latest['sale_price'] > 0 else 0
        
        score, reasons, profile = score_property(
            holding_years, latest['prop_type'], gain_pct, purchase_date.year
        )
        
        owners = [o for o in [latest['owner1'], latest['owner2']] if o and o != '-']
        
        result.append({
            'address': latest['address'],
            'suburb': latest['suburb'],
            'prop_type': latest['prop_type'],
            'beds': latest['beds'],
            'baths': latest['baths'],
            'land_size': latest['land_size'],
            'purchase_price': latest['sale_price'],
            'purchase_date': purchase_date.isoformat(),
            'purchase_year': purchase_date.year,
            'holding_years': holding_years,
            'estimated_value': estimated_value,
            'gain_estimate': gain_estimate,
            'gain_pct': gain_pct,
            'score': score,
            'profile': profile,
            'reasons': reasons,
            'owners': owners,
            'agency_bought_from': latest['agency'],
            'nb_past_sales': len(sales),
        })

    result.sort(key=lambda x: x['score'], reverse=True)
    
    output_file = 'data/prospects_data.json'
    with open(output_file, 'w') as f:
        json.dump(result, f, default=str, separators=(',',':'))
    
    hot = len([r for r in result if r['score'] >= 7])
    print(f"✓ {len(result)} propriétés scorées")
    print(f"✓ {hot} prospects chauds (score ≥ 7)")
    print(f"✓ Sauvegardé dans {output_file}")

if __name__ == '__main__':
    main()
