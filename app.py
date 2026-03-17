import streamlit as st
import pandas as pd
import math

class CreditRatingModel:
    def __init__(self):
        self.master_scale = [(90, 'AA'), (80, 'A'), (70, 'BBB'), (50, 'BB'), (0, 'CCC')]

    def calc_quantitative(self, net_borrowing, ebitda, interest_exp, total_liabilities, equity, 
                          total_borrowing, total_assets, operating_profit, quick_assets, 
                          current_liabilities, revenue, avg_ar):
        score = 0.0
        if ebitda <= 0: score += 0
        else:
            ratio_1 = net_borrowing / ebitda
            if ratio_1 < 1: score += 25
            elif 1 <= ratio_1 < 3: score += (25 - 5 * (ratio_1 - 1))
            elif 3 <= ratio_1 <= 6: score += (15 - 3.3 * (ratio_1 - 3))
            else: score += 0

        if interest_exp <= 0: score += 15 
        else:
            ratio_2 = ebitda / interest_exp
            if ratio_2 >= 3: score += 15
            elif 1 <= ratio_2 < 3: score += 7.5 * (ratio_2 - 1)
            else: score += 0

        if equity <= 0: score += 0 
        else:
            ratio_3 = (total_liabilities / equity) * 100
            if ratio_3 <= 100: score += 15
            elif 100 < ratio_3 <= 400: score += 15 - (15 * ((ratio_3 - 100) / 300))
            else: score += 0

        if total_assets <= 0: score += 0
        else:
            ratio_4 = (total_borrowing / total_assets) * 100
            if ratio_4 <= 30: score += 15
            elif 30 < ratio_4 <= 60: score += 15 - (15 * ((ratio_4 - 30) / 30))
            else: score += 0

        if total_assets <= 0: score += 0
        else:
            ratio_5 = (operating_profit / total_assets) * 100
            if ratio_5 >= 10: score += 15
            elif 0 <= ratio_5 < 10: score += 1.5 * ratio_5
            else: score += 0

        if current_liabilities <= 0: score += 10
        else:
            ratio_6 = (quick_assets / current_liabilities) * 100
            if ratio_6 >= 100: score += 10
            elif 50 <= ratio_6 < 100: score += 10 * ((ratio_6 - 50) / 50)
            else: score += 0

        if avg_ar <= 0: score += 5
        else:
            ratio_7 = revenue / avg_ar
            if ratio_7 >= 6: score += 5
            elif 3 <= ratio_7 < 6: score += 5 * ((ratio_7 - 3) / 3)
            else: score += 0

        return round(score * 0.6, 2)

    def calc_qualitative(self, ceo_exp_years, has_bad_history, tcb_grade, rnd_ratio, top3_dependency, irr_grade):
        score = 0.0
        if ceo_exp_years >= 15: score += 15
        elif 10 <= ceo_exp_years < 15: score += 12
        elif 5 <= ceo_exp_years < 10: score += 8
        else: score += 4
            
        if not has_bad_history: score += 20 

        if tcb_grade in ['T1', 'T2']: score += 20
        elif tcb_grade in ['T3', 'T4']: score += 16
        elif tcb_grade in ['T5', 'T6']: score += 10
        else: score += 4
            
        if rnd_ratio >= 5: score += 10
        elif 2 <= rnd_ratio < 5: score += 6
        else: score += 2

        score += 10 
        if top3_dependency < 30: score += 15
        elif 30 <= top3_dependency <= 50: score += 10
        elif 50 < top3_dependency <= 80: score += 4
        else: score += 0

        score += 10 
        if irr_grade == 1: score += 5
        elif irr_grade == 5: score -= 5

        score = min(score, 100.0)
        return round(score * 0.4, 2)

    def calc_final_rating(self, s_quant, s_qual, is_continuous_loss, is_capital_eroded, 
                          audit_opinion, recent_overdue, pat_rev_growth, tcb_grade):
        s_total = s_quant + s_qual
        alpha = -5.0
        beta = 0.1
        try:
            pd = 1 / (1 + math.exp(alpha + beta * s_total))
        except OverflowError:
            pd = 0.0001
        pd_percentage = round(pd * 100, 2)

        if audit_opinion in ['한정', '거절']:
            return "Reject", pd_percentage, "감사의견 거절/한정"
        if is_capital_eroded:
            return "D", pd_percentage, "완전 자본잠식"

        base_rating = 'CCC'
        for threshold, rating in self.master_scale:
            if s_total >= threshold:
                base_rating = rating
                break

        if is_continuous_loss:
            rating_precedence = {'AA': 1, 'A': 2, 'BBB': 3, 'BB': 4, 'B+': 5, 'CCC': 6}
            if rating_precedence.get(base_rating, 6) < rating_precedence['B+']:
                return 'B+', pd_percentage, "연속 적자 캡핑"

        final_rating = base_rating
        comment = "정상 산출"

        if base_rating == 'BB' and tcb_grade in ['T1', 'T2', 'T3'] and pat_rev_growth >= 30:
            final_rating = 'BBB-'
            comment = "+1 Notch 상향"
        elif base_rating == 'BBB' and recent_overdue:
            final_rating = 'BBB-'
            comment = "-1 Notch 하향"

        return final_rating, pd_percentage, comment


def get_notch_rank(rating):
    ranks = {'AA': 1, 'A': 2, 'BBB': 3, 'BBB-': 4, 'BB+': 5, 'BB': 6, 'B+': 7, 'CCC': 8, 'D': 9, 'Reject': 10}
    return ranks.get(rating, 11)


def main():
    st.set_page_config(page_title="CCRS 시뮬레이터", layout="wide")
    st.title("기업신용평가시스템(CCRS) 시뮬레이터")

    model = CreditRatingModel()

    st.sidebar.title("데이터 입력 세트")

    st.sidebar.header("A. 넉아웃 기초 데이터")
    audit_opinion = st.sidebar.selectbox("감사의견", ["적정", "한정", "거절"])
    continuous_loss = st.sidebar.selectbox("3년 연속 적자 여부", ["N", "Y"])
    capital_eroded = st.sidebar.selectbox("자본잠식 여부", ["N", "Y"])
    recent_overdue_input = st.sidebar.selectbox("최근 3개월 단기연체 이력(2회 이상)", ["N", "Y"])

    st.sidebar.header("B. 정량 평가 원시 데이터 (단위: 억 원)")
    net_borrowing = st.sidebar.number_input("순차입금", value=0)
    ebitda = st.sidebar.number_input("EBITDA", value=100)
    interest_exp = st.sidebar.number_input("이자비용", value=10)
    total_liabilities = st.sidebar.number_input("총부채", value=500)
    equity = st.sidebar.number_input("자기자본", value=500)
    total_borrowing = st.sidebar.number_input("총차입금", value=300)
    total_assets = st.sidebar.number_input("총자산", value=1000)
    operating_profit = st.sidebar.number_input("영업이익", value=80)
    quick_assets = st.sidebar.number_input("당좌자산", value=200)
    current_liabilities = st.sidebar.number_input("유동부채", value=150)
    revenue = st.sidebar.number_input("매출액", value=1000)
    avg_ar = st.sidebar.number_input("평균매출채권", value=100)

    st.sidebar.header("C. 정성 평가 원시 데이터")
    ceo_exp_years = st.sidebar.number_input("경영자 동업계 경력(년)", value=10)
    bad_history = st.sidebar.selectbox("경영진 소송/불량 이력", ["무", "유"])
    tcb_grade = st.sidebar.selectbox("외부 TCB 기술등급", ["T1", "T2", "T3", "T4", "T5", "T6", "T7 이하"], index=4)
    rnd_ratio = st.sidebar.number_input("R&D 투자 비율(%)", value=5.0)
    top3_dependency = st.sidebar.number_input("상위 3대 매출처 의존도(%)", value=30.0)
    irr_grade = st.sidebar.selectbox("산업위험등급(IRR)", [1, 2, 3, 4, 5], index=2)
    pat_rev_growth = st.sidebar.number_input("최근 1년 핵심 특허 매출 증가율(%)", value=0.0)

    is_continuous_loss = True if continuous_loss == "Y" else False
    is_capital_eroded = True if capital_eroded == "Y" else False
    has_bad_history = True if bad_history == "유" else False
    recent_overdue = True if recent_overdue_input == "Y" else False

    tab1, tab2 = st.tabs(["📊 기본 평가 (Base Case)", "⚡ 스트레스 테스트 (Stress Test)"])

    base_quant = model.calc_quantitative(net_borrowing, ebitda, interest_exp, total_liabilities, equity, 
                                         total_borrowing, total_assets, operating_profit, quick_assets, 
                                         current_liabilities, revenue, avg_ar)
    base_qual = model.calc_qualitative(ceo_exp_years, has_bad_history, tcb_grade, rnd_ratio, top3_dependency, irr_grade)
    base_rating, base_pd, base_comment = model.calc_final_rating(base_quant, base_qual, is_continuous_loss, 
                                                                 is_capital_eroded, audit_opinion, recent_overdue, 
                                                                 pat_rev_growth, tcb_grade)

    with tab1:
        st.subheader("Base Case 평가 결과")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="최종 산출 신용등급", value=base_rating)
        with col2:
            st.metric(label="예상 부도확률(PD)", value=f"{base_pd}%")

        st.markdown("---")
        score_df = pd.DataFrame({
            "평가 카테고리": ["정량 평가 (60점 만점)", "정성 평가 (40점 만점)"],
            "점수": [base_quant, base_qual]
        })
        st.bar_chart(score_df.set_index("평가 카테고리"), height=300)
        st.write(f"**총점:** {round(base_quant + base_qual, 2)} 점 / 100 점")

        if base_comment == "정상 산출":
            st.success("특이사항 없음: 정상적인 가중 평균 산출이 완료되었습니다.")
        elif base_rating in ["Reject", "D"] or "캡핑" in base_comment:
            st.error(f"[넉아웃 룰 발동] {base_comment}")
        else:
            st.warning(f"[노칭 룰 발동] {base_comment}")

    with tab2:
        st.subheader("거시경제/재무 충격 시나리오 적용")
        st.write("선택한 충격 변수를 기본 데이터에 반영하여 신용등급 변동을 시뮬레이션합니다.")
        
        shock_1 = st.checkbox("충격 1: 매출채권 2배 증가 (활동성 지표 악화)")
        shock_2 = st.checkbox("충격 2: 산업위험등급(IRR) 2단계 강등 (거시환경 악화)")

        stress_avg_ar = avg_ar * 2 if shock_1 else avg_ar
        stress_irr_grade = min(irr_grade + 2, 5) if shock_2 else irr_grade

        if st.button("스트레스 테스트 실행", use_container_width=True):
            stress_quant = model.calc_quantitative(net_borrowing, ebitda, interest_exp, total_liabilities, equity, 
                                                 total_borrowing, total_assets, operating_profit, quick_assets, 
                                                 current_liabilities, revenue, stress_avg_ar)
            stress_qual = model.calc_qualitative(ceo_exp_years, has_bad_history, tcb_grade, rnd_ratio, top3_dependency, stress_irr_grade)
            stress_rating, stress_pd, stress_comment = model.calc_final_rating(stress_quant, stress_qual, is_continuous_loss, 
                                                                               is_capital_eroded, audit_opinion, recent_overdue, 
                                                                               pat_rev_growth, tcb_grade)

            base_rank = get_notch_rank(base_rating)
            stress_rank = get_notch_rank(stress_rating)
            notch_diff = base_rank - stress_rank

            st.markdown("---")
            st.subheader("스트레스 테스트 결과 비교")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Base Case 등급", value=base_rating, delta=f"PD: {base_pd}%", delta_color="off")
            with col2:
                st.metric(label="Stress Case 등급", value=stress_rating, delta=f"PD: {stress_pd}%", delta_color="inverse")
            with col3:
                if notch_diff < 0:
                    st.error(f"등급 하락: {base_rating} ➔ {stress_rating} ({notch_diff} Notch)")
                elif notch_diff > 0:
                    st.success(f"등급 상승: {base_rating} ➔ {stress_rating} (+{notch_diff} Notch)")
                else:
                    st.info("등급 변동 없음")

            st.markdown("##### 점수 변동 내역")
            diff_df = pd.DataFrame({
                "항목": ["정량 점수", "정성 점수", "총점"],
                "Base Case": [base_quant, base_qual, round(base_quant + base_qual, 2)],
                "Stress Case": [stress_quant, stress_qual, round(stress_quant + stress_qual, 2)]
            })
            st.dataframe(diff_df, use_container_width=True)
            
            if stress_comment != "정상 산출":
                st.warning(f"Stress Case 특이사항: {stress_comment}")

if __name__ == "__main__":
    main()