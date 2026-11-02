import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from src.predict import predict_risk, explain, validate, level, LOW, HIGH

BASE = dict(age=55, sex=1, cp=0, trestbps=130, chol=240, fbs=0, restecg=1, thalach=150, exang=0, oldpeak=1.0, slope=1, ca=0, thal=2)

def test_probability_in_range():
    p, lv = predict_risk(BASE)
    assert 0 <= p <= 1 and lv in ("Thấp", "Trung bình", "Cao")

def test_high_risk_case_scores_higher_than_low_risk_case():
    low = BASE | dict(age=35, cp=2, thalach=185, oldpeak=0.0, ca=0, thal=2, exang=0, slope=2)
    high = BASE | dict(age=62, cp=0, thalach=110, oldpeak=3.5, ca=3, thal=3, exang=1, slope=0)
    assert predict_risk(high)[0] > predict_risk(low)[0]

@pytest.mark.parametrize("bad", [dict(age="abc"), dict(age=300), dict(thal=0), dict(sex=2), dict(oldpeak=-1)])
def test_invalid_input_rejected(bad):
    with pytest.raises(ValueError):
        predict_risk(BASE | bad)

def test_missing_field_rejected():
    d = dict(BASE); d.pop("chol")
    with pytest.raises(ValueError):
        predict_risk(d)

def test_level_thresholds():
    assert level(LOW - 0.01) == "Thấp" and level(LOW) == "Trung bình" and level(HIGH) == "Cao"

def test_explanation_covers_all_features_and_is_finite():
    ex = explain(BASE)
    assert len(ex) == 13 and ex.notna().all()
